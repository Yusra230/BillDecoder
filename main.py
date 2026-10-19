import argparse
import csv
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

from core.config import (
    TRAIN_BILLS_DIR,
    TEST_BILLS_DIR,
    OUTPUT_DIR,
    REQUEST_DELAY_SECONDS,
)
from core.extractor import extract_bill_data
from core.qa_engine import answer_questions_batch
from core.csv_writer import write_level1_csv, write_level2_csv
from core.validator import validate_level1_csv, validate_level2_csv


def find_bill_file(bills_dir: Path, bill_id: str) -> Path:
    """Find the image file matching bill_id regardless of extension."""
    for ext in [".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"]:
        p = bills_dir / f"{bill_id}{ext}"
        if p.exists():
            return p
    # Search glob
    matches = list(bills_dir.glob(f"{bill_id}.*"))
    if matches:
        return matches[0]
    raise FileNotFoundError(f"No image found for bill_id '{bill_id}' in {bills_dir}")


def main():
    parser = argparse.ArgumentParser(description="WTQ 2026 Utility Bill Decoder")
    parser.add_argument(
        "--mode",
        choices=["auto", "test", "train"],
        default="auto",
        help="Execution mode (auto detects test data if present, otherwise train)",
    )
    parser.add_argument(
        "--bills-dir",
        type=Path,
        default=None,
        help="Custom bills directory",
    )
    parser.add_argument(
        "--template-dir",
        type=Path,
        default=None,
        help="Directory containing level1.csv and level2.csv templates",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory to write output CSVs",
    )
    args = parser.parse_args()

    # Determine paths based on mode
    test_csv_dir = Path("test/csv")
    if args.mode == "test" or (args.mode == "auto" and test_csv_dir.exists() and (test_csv_dir / "level1.csv").exists()):
        mode = "test"
        bills_dir = args.bills_dir or TEST_BILLS_DIR
        template_dir = args.template_dir or test_csv_dir
        print("[INFO] Running in TEST mode with official test data & templates.")
    else:
        mode = "train"
        bills_dir = args.bills_dir or TRAIN_BILLS_DIR
        template_dir = args.template_dir
        print("[INFO] Running in TRAIN mode with sample training bills.")

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    l1_output_csv = output_dir / "level1.csv"
    l2_output_csv = output_dir / "level2.csv"

    # 1. Determine list of bill IDs and files
    bill_files: Dict[str, Path] = {}
    l1_rows_template = []
    if template_dir and (template_dir / "level1.csv").exists():
        with open(template_dir / "level1.csv", mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if row:
                    bid = row[0].strip()
                    l1_rows_template.append(bid)
                    bill_files[bid] = find_bill_file(bills_dir, bid)
    else:
        # Fallback to scanning bills_dir
        for p in sorted(bills_dir.glob("*.*")):
            if p.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                bill_files[p.stem] = p
                l1_rows_template.append(p.stem)

    print(f"[INFO] Total bills to process: {len(bill_files)}")
    print(f"[INFO] Bill IDs: {list(bill_files.keys())}")

    # 2. Extract Level 1 and internal history for each bill
    extracted_l1_data: Dict[str, dict] = {}
    extracted_history: Dict[str, list] = {}

    print("\n" + "=" * 60)
    print("PHASE 1: LEVEL 1 EXTRACTION")
    print("=" * 60)

    for idx, (bid, img_path) in enumerate(bill_files.items(), 1):
        print(f"[{idx}/{len(bill_files)}] Processing Level 1 for {bid} ({img_path.name})...")
        l1_clean, raw = extract_bill_data(img_path)
        extracted_l1_data[bid] = l1_clean
        extracted_history[bid] = raw.get("history", [])

        print(f"   Done -> Provider: {l1_clean.get('provider')}, Units: {l1_clean.get('units_consumed')}, Month: {l1_clean.get('bill_month')}")

        if idx < len(bill_files):
            time.sleep(REQUEST_DELAY_SECONDS)

    # Write Level 1 CSV
    l1_csv_rows = [{"bill_id": bid, "json": extracted_l1_data[bid]} for bid in l1_rows_template]
    write_level1_csv(l1_output_csv, l1_csv_rows)
    print(f"\n[SUCCESS] Wrote Level 1 results to {l1_output_csv} ({len(l1_csv_rows)} rows)")

    # 3. Process Level 2 Questions
    print("\n" + "=" * 60)
    print("PHASE 2: LEVEL 2 QUESTION ANSWERING")
    print("=" * 60)

    template_l2_rows = []
    if template_dir and (template_dir / "level2.csv").exists():
        with open(template_dir / "level2.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                template_l2_rows.append(r)
    else:
        # If no template provided (e.g. running on train), use sample questions
        sample_q = [
            ("Q1", "How much of my bill is taxes?"),
            ("Q2", "How many months in my history went above 200 units?"),
        ]
        for bid in l1_rows_template:
            for qid, qtext in sample_q:
                template_l2_rows.append({
                    "bill_id": bid,
                    "question_id": qid,
                    "question": qtext,
                    "answer": "",
                })

    print(f"[INFO] Total Level 2 questions to answer: {len(template_l2_rows)}")

    # Group questions by bill_id for batched processing
    questions_by_bill: Dict[str, List[dict]] = {}
    for r in template_l2_rows:
        bid = r["bill_id"]
        if bid not in questions_by_bill:
            questions_by_bill[bid] = []
        questions_by_bill[bid].append({"question_id": r["question_id"], "question": r["question"]})

    # Answer questions per bill
    answers_map: Dict[str, Dict[str, str]] = {}
    bill_count = len(questions_by_bill)

    for idx, (bid, qlist) in enumerate(questions_by_bill.items(), 1):
        img_path = bill_files[bid]
        l1_data = extracted_l1_data[bid]
        hist_data = extracted_history.get(bid, [])

        print(f"[{idx}/{bill_count}] Answering {len(qlist)} questions for {bid}...")
        bill_answers = answer_questions_batch(img_path, l1_data, hist_data, qlist)
        answers_map[bid] = bill_answers

        if idx < bill_count:
            time.sleep(REQUEST_DELAY_SECONDS)

    # Populate final Level 2 rows maintaining exact template order
    final_l2_rows = []
    for r in template_l2_rows:
        bid = r["bill_id"]
        qid = r["question_id"]
        ans = answers_map.get(bid, {}).get(qid, "Information is not available on the bill.")
        final_l2_rows.append({
            "bill_id": bid,
            "question_id": qid,
            "question": r["question"],
            "answer": ans,
        })

    write_level2_csv(l2_output_csv, final_l2_rows)
    print(f"\n[SUCCESS] Wrote Level 2 results to {l2_output_csv} ({len(final_l2_rows)} rows)")

    # 4. Validation Phase
    print("\n" + "=" * 60)
    print("PHASE 3: OUTPUT INTEGRITY VALIDATION")
    print("=" * 60)

    l1_ok, l1_errs = validate_level1_csv(l1_output_csv, expected_rows=len(l1_rows_template))
    if l1_ok:
        print(f" [PASS] level1.csv is valid ({len(l1_rows_template)} rows).")
    else:
        print(f" [FAIL] level1.csv validation issues:")
        for e in l1_errs:
            print(f"   - {e}")

    l2_ok, l2_errs = validate_level2_csv(l2_output_csv, expected_rows=len(final_l2_rows))
    if l2_ok:
        print(f" [PASS] level2.csv is valid ({len(final_l2_rows)} rows, no empty answers).")
    else:
        print(f" [FAIL] level2.csv validation issues:")
        for e in l2_errs:
            print(f"   - {e}")

    if l1_ok and l2_ok:
        print("\n ALL VALIDATIONS PASSED! Output CSVs ready for submission.")
    else:
        print("\n WARNING: Some validation checks failed. Review errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
