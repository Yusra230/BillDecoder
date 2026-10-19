import os
import json
import uuid
import time
import shutil
import hashlib
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from core.config import (
    BASE_DIR,
    MODEL_NAME,
    REQUEST_DELAY_SECONDS,
)
from core.extractor import extract_bill_data
from core.qa_engine import answer_questions_batch
from core.schemas import format_bill_dict

# Upload and storage directory
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
INDEX_FILE = UPLOADS_DIR / "bills_index.json"

app = FastAPI(
    title="AI Utility Bill Decoder API",
    description="Backend API for AI-Powered Utility Bill Extraction and Q&A",
    version="1.0.0",
)

# Configure CORS for local development (Vite dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Concurrency locks
gemini_lock = asyncio.Lock()
upload_lock = asyncio.Lock()
last_api_call_time = 0.0

SUPPORTED_PROVIDERS = {"KE", "LESCO", "IESCO"}


async def throttle_gemini_call():
    """Ensure at least REQUEST_DELAY_SECONDS between calls to avoid 429 errors."""
    global last_api_call_time
    now = time.time()
    elapsed = now - last_api_call_time
    if elapsed < REQUEST_DELAY_SECONDS:
        await asyncio.sleep(REQUEST_DELAY_SECONDS - elapsed)
    last_api_call_time = time.time()


def get_file_sha256(content: bytes) -> str:
    """Calculates SHA-256 digest of binary content."""
    return hashlib.sha256(content).hexdigest()


def compute_disk_file_hash(file_path: Path) -> Optional[str]:
    """Computes SHA-256 digest of a file on disk."""
    if not file_path.exists():
        return None
    try:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None


def validate_extracted_bill(level1_data: Dict[str, Any], raw_data: Dict[str, Any] = None) -> Tuple[bool, str]:
    """
    Explicitly determines whether the extracted data establishes a supported electricity bill
    from KE, LESCO, or IESCO. Rejects non-bill images, empty extractions, and materially incomplete data.
    """
    if not isinstance(level1_data, dict):
        return False, "This doesn't appear to be a supported electricity bill. Please upload a valid KE, LESCO, or IESCO bill image."

    # 1. Provider must be one of the three supported Pakistani electricity distributors
    provider = level1_data.get("provider")
    if not provider or provider not in SUPPORTED_PROVIDERS:
        return False, "This doesn't appear to be a supported electricity bill. Please upload a valid KE, LESCO, or IESCO bill image."

    # 2. Must establish a billing period or date
    dates = [
        level1_data.get("bill_month"),
        level1_data.get("due_date"),
        level1_data.get("issue_date"),
        level1_data.get("reading_date"),
    ]
    has_date = any(bool(d and isinstance(d, str) and d.strip()) for d in dates)
    if not has_date:
        return False, "This doesn't appear to be a supported electricity bill. Please upload a valid KE, LESCO, or IESCO bill image."

    # 3. Must establish electricity consumption or metering
    units = level1_data.get("units_consumed")
    prev_r = level1_data.get("previous_reading")
    curr_r = level1_data.get("current_reading")
    has_metering = (
        (units is not None and isinstance(units, (int, float)) and units >= 0)
        or (
            prev_r is not None
            and curr_r is not None
            and isinstance(prev_r, (int, float))
            and isinstance(curr_r, (int, float))
        )
    )
    if not has_metering:
        return False, "This doesn't appear to be a supported electricity bill. Please upload a valid KE, LESCO, or IESCO bill image."

    # 4. Must establish a financial settlement or charge figure
    financial_fields = [
        level1_data.get("payable_within_due_date"),
        level1_data.get("current_bill"),
        level1_data.get("total_charges"),
        level1_data.get("payable_after_due_date"),
    ]
    has_financials = any(
        f is not None and isinstance(f, (int, float)) for f in financial_fields
    )
    if not has_financials:
        return False, "This doesn't appear to be a supported electricity bill. Please upload a valid KE, LESCO, or IESCO bill image."

    # 5. Density check: A legitimate bill from KE, LESCO, or IESCO has multiple fields populated.
    vital_fields = [
        "tariff",
        "sanctioned_load_kw",
        "bill_month",
        "reading_date",
        "issue_date",
        "due_date",
        "previous_reading",
        "current_reading",
        "units_consumed",
        "total_charges",
        "total_taxes",
        "current_bill",
        "payable_within_due_date",
        "payable_after_due_date",
    ]
    populated_count = sum(1 for vf in vital_fields if level1_data.get(vf) is not None)
    if populated_count < 4:
        return False, "This doesn't appear to be a supported electricity bill. Please upload a valid KE, LESCO, or IESCO bill image."

    return True, ""


def find_duplicate_by_hash(file_hash: str, index: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Checks if an exact file with this SHA-256 hash has already been stored."""
    if not file_hash:
        return None

    for bill in index:
        # Check direct hash
        if bill.get("file_hash") == file_hash:
            bill_folder = UPLOADS_DIR / bill["bill_id"]
            if (bill_folder / "level1.json").exists():
                return bill
        # Check additional alias hashes
        if file_hash in bill.get("additional_hashes", []):
            bill_folder = UPLOADS_DIR / bill["bill_id"]
            if (bill_folder / "level1.json").exists():
                return bill
    return None


def find_semantic_duplicate(
    new_level1: Dict[str, Any], index: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Detects whether the newly extracted bill is the exact same bill as an existing record,
    even if uploaded with a different filename or different image encoding.
    Conservative: Only merges when there is high-confidence, unique physical proof (e.g. matching physical meter readings).
    """
    prov = new_level1.get("provider")
    month = new_level1.get("bill_month")
    units = new_level1.get("units_consumed")
    payable = new_level1.get("payable_within_due_date")
    prev_r = new_level1.get("previous_reading")
    curr_r = new_level1.get("current_reading")
    due_d = new_level1.get("due_date")

    # If critical core identifiers are missing, do not attempt semantic match
    if not prov or not month or units is None or payable is None:
        return None

    for item in index:
        if item.get("provider") != prov or item.get("bill_month") != month:
            continue
        if item.get("units_consumed") != units or item.get("payable_within_due_date") != payable:
            continue

        # Load existing level1 to compare detailed readings and charges
        b_id = item.get("bill_id")
        l1_path = UPLOADS_DIR / b_id / "level1.json"
        if not l1_path.exists():
            continue
        try:
            with open(l1_path, "r", encoding="utf-8") as f:
                exist_l1 = json.load(f)
        except Exception:
            continue

        # Proof A: Cumulative physical meter readings match (odometer counters are unique to that meter)
        if (
            prev_r is not None
            and curr_r is not None
            and exist_l1.get("previous_reading") is not None
            and exist_l1.get("current_reading") is not None
        ):
            if (
                exist_l1.get("previous_reading") == prev_r
                and exist_l1.get("current_reading") == curr_r
            ):
                return item

        # Proof B: When readings are not both printed, require matching due date, tariff, sanctioned load, and total charges/taxes
        if due_d and exist_l1.get("due_date") == due_d:
            if (
                new_level1.get("tariff")
                and exist_l1.get("tariff") == new_level1.get("tariff")
                and new_level1.get("sanctioned_load_kw") is not None
                and exist_l1.get("sanctioned_load_kw") == new_level1.get("sanctioned_load_kw")
                and new_level1.get("total_charges") is not None
                and exist_l1.get("total_charges") == new_level1.get("total_charges")
                and new_level1.get("total_taxes") is not None
                and exist_l1.get("total_taxes") == new_level1.get("total_taxes")
            ):
                return item

    return None


def read_index() -> List[Dict[str, Any]]:
    """Reads index, sanitizes incomplete/corrupted entries, and backfills file hashes."""
    if not INDEX_FILE.exists():
        return []
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            raw_index = json.load(f)
    except Exception:
        return []

    sanitized = []
    seen_ids = set()
    seen_hashes = set()
    needs_rewrite = False

    for item in raw_index:
        b_id = item.get("bill_id")
        if not b_id or b_id in seen_ids:
            needs_rewrite = True
            continue

        # Sanitize: reject entries with empty or materially incomplete extractions
        if (
            item.get("units_consumed") is None
            and item.get("bill_month") is None
            and item.get("payable_within_due_date") is None
            and item.get("due_date") is None
        ):
            # Clean up orphaned folder if it was an empty extraction
            shutil.rmtree(UPLOADS_DIR / b_id, ignore_errors=True)
            needs_rewrite = True
            continue

        # Backfill file_hash if missing
        if "file_hash" not in item:
            b_folder = UPLOADS_DIR / b_id
            img_name = item.get("image_file", "image.png")
            img_p = b_folder / img_name
            if not img_p.exists():
                for ext in [".png", ".jpg", ".jpeg"]:
                    cand = b_folder / f"image{ext}"
                    if cand.exists():
                        img_p = cand
                        break
            computed_h = compute_disk_file_hash(img_p)
            if computed_h:
                item["file_hash"] = computed_h
                needs_rewrite = True

        f_hash = item.get("file_hash")
        if f_hash and f_hash in seen_hashes:
            # Duplicate historical storage record
            shutil.rmtree(UPLOADS_DIR / b_id, ignore_errors=True)
            needs_rewrite = True
            continue
        if f_hash:
            seen_hashes.add(f_hash)

        seen_ids.add(b_id)
        sanitized.append(item)

    if needs_rewrite:
        write_index(sanitized)

    return sanitized


def write_index(index: List[Dict[str, Any]]):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


def save_bill_record(
    bill_id: str,
    original_filename: str,
    image_ext: str,
    level1_data: Dict[str, Any],
    history_data: List[Dict[str, Any]],
    file_hash: Optional[str] = None,
):
    bill_folder = UPLOADS_DIR / bill_id
    bill_folder.mkdir(parents=True, exist_ok=True)

    with open(bill_folder / "level1.json", "w", encoding="utf-8") as f:
        json.dump(level1_data, f, indent=2, ensure_ascii=False)

    with open(bill_folder / "history.json", "w", encoding="utf-8") as f:
        json.dump(history_data, f, indent=2, ensure_ascii=False)

    metadata = {
        "bill_id": bill_id,
        "original_filename": original_filename,
        "image_file": f"image{image_ext}",
        "file_hash": file_hash,
        "additional_hashes": [],
        "provider": level1_data.get("provider"),
        "tariff": level1_data.get("tariff"),
        "bill_month": level1_data.get("bill_month"),
        "due_date": level1_data.get("due_date"),
        "units_consumed": level1_data.get("units_consumed"),
        "current_bill": level1_data.get("current_bill"),
        "total_charges": level1_data.get("total_charges"),
        "total_taxes": level1_data.get("total_taxes"),
        "payable_within_due_date": level1_data.get("payable_within_due_date"),
        "payable_after_due_date": level1_data.get("payable_after_due_date"),
        "status": "ready",
        "uploaded_at": datetime.now().isoformat(),
    }

    with open(bill_folder / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    index = read_index()
    index = [b for b in index if b.get("bill_id") != bill_id]
    index.insert(0, metadata)
    write_index(index)
    return metadata


# Request / Response Schemas
class QuestionItem(BaseModel):
    question_id: Optional[str] = None
    question: str


class AskRequest(BaseModel):
    question: Optional[str] = None
    questions: Optional[List[QuestionItem]] = None


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Utility Bill Decoder API",
        "model": MODEL_NAME,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/bills")
def list_bills():
    """Returns list of processed bills sorted with newest first."""
    return read_index()


@app.get("/api/bills/{bill_id}")
def get_bill_detail(bill_id: str):
    bill_folder = UPLOADS_DIR / bill_id
    if not bill_folder.exists():
        raise HTTPException(status_code=404, detail="Bill not found")

    meta_file = bill_folder / "metadata.json"
    l1_file = bill_folder / "level1.json"
    hist_file = bill_folder / "history.json"
    qa_file = bill_folder / "qa_history.json"

    if not (meta_file.exists() and l1_file.exists()):
        raise HTTPException(status_code=404, detail="Bill data incomplete")

    with open(meta_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    with open(l1_file, "r", encoding="utf-8") as f:
        level1 = json.load(f)

    history = []
    if hist_file.exists():
        with open(hist_file, "r", encoding="utf-8") as f:
            history = json.load(f)

    qa_history = []
    if qa_file.exists():
        with open(qa_file, "r", encoding="utf-8") as f:
            qa_history = json.load(f)

    return {
        "metadata": metadata,
        "level1": level1,
        "history": history,
        "qa_history": qa_history,
    }


@app.get("/api/bills/{bill_id}/image")
def get_bill_image(bill_id: str):
    bill_folder = UPLOADS_DIR / bill_id
    if not bill_folder.exists():
        raise HTTPException(status_code=404, detail="Bill not found")

    meta_file = bill_folder / "metadata.json"
    if not meta_file.exists():
        raise HTTPException(status_code=404, detail="Bill metadata not found")

    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    img_name = meta.get("image_file", "image.png")
    img_path = bill_folder / img_name
    if not img_path.exists():
        for ext in [".png", ".jpg", ".jpeg"]:
            candidate = bill_folder / f"image{ext}"
            if candidate.exists():
                img_path = candidate
                break

    if not img_path.exists():
        raise HTTPException(status_code=404, detail="Image file not found on disk")

    media_type = "image/png"
    if img_path.suffix.lower() in [".jpg", ".jpeg"]:
        media_type = "image/jpeg"

    return FileResponse(img_path, media_type=media_type)


@app.post("/api/bills/upload")
async def upload_bill(file: UploadFile = File(...)):
    """
    Uploads a bill image, protects against duplicate records, explicitly determines
    if the image is a supported electricity bill, and extracts Level 1 and usage history.
    """
    valid_exts = [".png", ".jpg", ".jpeg"]
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in valid_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension {file_ext}. Allowed: .png, .jpg, .jpeg",
        )

    # Read binary bytes for validation and hashing
    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(file_bytes) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 15 MB limit.")

    file_hash = get_file_sha256(file_bytes)

    # 1. Fast Pre-Extraction Duplicate Check (concurrency-safe)
    async with upload_lock:
        index = read_index()
        exact_dup = find_duplicate_by_hash(file_hash, index)
        if exact_dup:
            b_id = exact_dup["bill_id"]
            b_folder = UPLOADS_DIR / b_id
            with open(b_folder / "level1.json", "r", encoding="utf-8") as f:
                l1 = json.load(f)
            hist = []
            if (b_folder / "history.json").exists():
                with open(b_folder / "history.json", "r", encoding="utf-8") as f:
                    hist = json.load(f)

            return {
                "success": True,
                "bill_id": b_id,
                "metadata": exact_dup,
                "level1": l1,
                "history": hist,
                "duplicate": True,
                "message": "Duplicate statement detected. Returning existing bill record.",
            }

    # Save to a temporary bill folder during extraction
    bill_id = f"bill_{uuid.uuid4().hex[:8]}"
    bill_folder = UPLOADS_DIR / bill_id
    bill_folder.mkdir(parents=True, exist_ok=True)
    image_path = bill_folder / f"image{file_ext}"

    try:
        with open(image_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        shutil.rmtree(bill_folder, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")

    # Process extraction with Gemini multimodal model
    async with gemini_lock:
        await throttle_gemini_call()
        try:
            level1_clean, raw_data = await asyncio.to_thread(extract_bill_data, image_path)
        except Exception as e:
            shutil.rmtree(bill_folder, ignore_errors=True)
            raise HTTPException(
                status_code=500,
                detail=f"AI extraction failed: {str(e)}",
            )

    # 2. Validation Check: Explicitly determine whether image is a supported electricity bill
    is_valid, validation_err = validate_extracted_bill(level1_clean, raw_data)
    if not is_valid:
        # Clean up temporary folder completely so no record or index entry exists
        shutil.rmtree(bill_folder, ignore_errors=True)
        raise HTTPException(
            status_code=422,
            detail="This doesn't appear to be a supported electricity bill. Please upload a valid KE, LESCO, or IESCO bill image.",
        )

    # 3. Post-Extraction Duplicate Check (concurrency & semantic check)
    async with upload_lock:
        index = read_index()

        # Check if an exact duplicate was completed concurrently
        concurrent_dup = find_duplicate_by_hash(file_hash, index)
        if concurrent_dup:
            shutil.rmtree(bill_folder, ignore_errors=True)
            b_id = concurrent_dup["bill_id"]
            b_folder = UPLOADS_DIR / b_id
            with open(b_folder / "level1.json", "r", encoding="utf-8") as f:
                l1 = json.load(f)
            hist = []
            if (b_folder / "history.json").exists():
                with open(b_folder / "history.json", "r", encoding="utf-8") as f:
                    hist = json.load(f)
            return {
                "success": True,
                "bill_id": b_id,
                "metadata": concurrent_dup,
                "level1": l1,
                "history": hist,
                "duplicate": True,
                "message": "Duplicate statement detected. Returning existing bill record.",
            }

        # Check if a semantic duplicate exists (same bill under different filename or re-encoding)
        semantic_dup = find_semantic_duplicate(level1_clean, index)
        if semantic_dup:
            shutil.rmtree(bill_folder, ignore_errors=True)
            b_id = semantic_dup["bill_id"]
            # Register this new hash into existing record's additional_hashes
            hashes = semantic_dup.get("additional_hashes", [])
            if file_hash not in hashes and file_hash != semantic_dup.get("file_hash"):
                hashes.append(file_hash)
                semantic_dup["additional_hashes"] = hashes
                write_index(index)
                with open(UPLOADS_DIR / b_id / "metadata.json", "w", encoding="utf-8") as f:
                    json.dump(semantic_dup, f, indent=2, ensure_ascii=False)

            b_folder = UPLOADS_DIR / b_id
            with open(b_folder / "level1.json", "r", encoding="utf-8") as f:
                l1 = json.load(f)
            hist = []
            if (b_folder / "history.json").exists():
                with open(b_folder / "history.json", "r", encoding="utf-8") as f:
                    hist = json.load(f)

            return {
                "success": True,
                "bill_id": b_id,
                "metadata": semantic_dup,
                "level1": l1,
                "history": hist,
                "duplicate": True,
                "message": "Duplicate statement detected (matches existing bill records).",
            }

        # 4. Brand-new unique bill -> persist record and update index
        history = raw_data.get("history", [])
        metadata = save_bill_record(
            bill_id=bill_id,
            original_filename=file.filename,
            image_ext=file_ext,
            level1_data=level1_clean,
            history_data=history,
            file_hash=file_hash,
        )

    return {
        "success": True,
        "bill_id": bill_id,
        "metadata": metadata,
        "level1": level1_clean,
        "history": history,
        "duplicate": False,
    }


@app.post("/api/bills/{bill_id}/ask")
async def ask_bill_question(bill_id: str, request: AskRequest):
    """Answers customer questions grounded in the extracted bill and bill image."""
    bill_folder = UPLOADS_DIR / bill_id
    if not bill_folder.exists():
        raise HTTPException(status_code=404, detail="Bill not found")

    meta_file = bill_folder / "metadata.json"
    l1_file = bill_folder / "level1.json"
    hist_file = bill_folder / "history.json"

    if not (meta_file.exists() and l1_file.exists()):
        raise HTTPException(status_code=404, detail="Bill data incomplete")

    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    with open(l1_file, "r", encoding="utf-8") as f:
        level1_data = json.load(f)

    history_data = []
    if hist_file.exists():
        with open(hist_file, "r", encoding="utf-8") as f:
            history_data = json.load(f)

    img_name = meta.get("image_file", "image.png")
    img_path = bill_folder / img_name
    if not img_path.exists():
        raise HTTPException(status_code=404, detail="Source bill image missing")

    # Build question batch
    questions_to_ask = []
    if request.questions:
        for idx, q_obj in enumerate(request.questions, 1):
            qid = q_obj.question_id or f"Q{idx}"
            questions_to_ask.append({"question_id": qid, "question": q_obj.question})
    elif request.question:
        questions_to_ask.append({"question_id": "Q1", "question": request.question})
    else:
        raise HTTPException(status_code=400, detail="Must provide either 'question' or 'questions'")

    async with gemini_lock:
        await throttle_gemini_call()
        try:
            answers_map = await asyncio.to_thread(
                answer_questions_batch,
                img_path,
                level1_data,
                history_data,
                questions_to_ask,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"QA Engine failed to generate answers: {str(e)}",
            )

    # Update QA history cache
    qa_file = bill_folder / "qa_history.json"
    qa_history = []
    if qa_file.exists():
        try:
            with open(qa_file, "r", encoding="utf-8") as f:
                qa_history = json.load(f)
        except Exception:
            qa_history = []

    timestamp = datetime.now().isoformat()
    new_qa_entries = []
    for q_item in questions_to_ask:
        qid = q_item["question_id"]
        q_text = q_item["question"]
        ans = answers_map.get(qid, "Information not available on bill.")
        entry = {
            "question_id": qid,
            "question": q_text,
            "answer": ans,
            "answered_at": timestamp,
        }
        new_qa_entries.append(entry)
        qa_history.append(entry)

    with open(qa_file, "w", encoding="utf-8") as f:
        json.dump(qa_history, f, indent=2, ensure_ascii=False)

    return {
        "success": True,
        "bill_id": bill_id,
        "answers": answers_map,
        "entries": new_qa_entries,
    }


@app.delete("/api/bills/{bill_id}")
def delete_bill(bill_id: str):
    bill_folder = UPLOADS_DIR / bill_id
    if not bill_folder.exists():
        raise HTTPException(status_code=404, detail="Bill not found")

    shutil.rmtree(bill_folder, ignore_errors=True)

    index = read_index()
    index = [b for b in index if b.get("bill_id") != bill_id]
    write_index(index)

    return {"success": True, "deleted_id": bill_id}


@app.get("/api/bills/{bill_id}/export")
def export_bill_json(bill_id: str):
    bill_folder = UPLOADS_DIR / bill_id
    l1_file = bill_folder / "level1.json"
    if not l1_file.exists():
        raise HTTPException(status_code=404, detail="Bill JSON not found")

    return FileResponse(
        l1_file,
        media_type="application/json",
        filename=f"{bill_id}_level1.json",
    )


# Serve compiled frontend in production if built
from fastapi.staticfiles import StaticFiles

DIST_DIR = BASE_DIR / "frontend" / "dist"
if DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(DIST_DIR), html=True), name="frontend")
