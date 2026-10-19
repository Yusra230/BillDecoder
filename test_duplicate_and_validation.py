import os
import json
import shutil
import hashlib
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from fastapi.testclient import TestClient

import api
from api import app, UPLOADS_DIR, INDEX_FILE, read_index, write_index

client = TestClient(app)


def create_dummy_image(color=(200, 200, 200), size=(100, 100)) -> bytes:
    """Helper to generate dummy PNG bytes."""
    buf = BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format="PNG")
    return buf.getvalue()


def run_all_tests():
    print("=" * 70)
    print("RUNNING AUTOMATED TEST SUITE: BILL VALIDATION & DEDUPLICATION")
    print("=" * 70)

    # Backup existing index for restoration if needed
    initial_index = read_index()
    initial_count = len(initial_index)

    # -------------------------------------------------------------
    # TEST 1: Random unrelated image is rejected (422) & no bill record created
    # -------------------------------------------------------------
    print("\n[TEST 1] Testing rejection of unrelated non-bill image...")
    cat_bytes = create_dummy_image(color=(255, 0, 0))

    # Mock extraction returning what an unrelated image typically produces (all nulls or missing provider)
    mock_unrelated_l1 = {
        "provider": "KE",
        "tariff": None,
        "sanctioned_load_kw": None,
        "bill_month": None,
        "reading_date": None,
        "issue_date": None,
        "due_date": None,
        "previous_reading": None,
        "current_reading": None,
        "units_consumed": None,
        "charges": [],
        "total_charges": None,
        "taxes": [],
        "total_taxes": None,
        "current_bill": None,
        "arrears": None,
        "payable_within_due_date": None,
        "payable_after_due_date": None,
    }
    mock_unrelated_raw = {"level1": mock_unrelated_l1, "history": []}

    with patch("api.extract_bill_data", return_value=(mock_unrelated_l1, mock_unrelated_raw)):
        res = client.post(
            "/api/bills/upload",
            files={"file": ("unrelated_photo.png", cat_bytes, "image/png")}
        )

    assert res.status_code == 422, f"Expected 422 for unrelated image, got {res.status_code}: {res.text}"
    detail = res.json().get("detail", "")
    assert "This doesn't appear to be a supported electricity bill" in detail, f"Unexpected error detail: {detail}"
    print(" [PASS] Unrelated image rejected with HTTP 422 and friendly guidance message.")

    # -------------------------------------------------------------
    # TEST 7: Rejected upload does not appear in dashboard or bill index
    # -------------------------------------------------------------
    print("\n[TEST 7] Verifying rejected upload does not appear in index or bills list...")
    index_after_reject = read_index()
    assert len(index_after_reject) == initial_count, "Index count changed after rejected upload!"
    bills_res = client.get("/api/bills")
    assert bills_res.status_code == 200
    listed_bills = bills_res.json()
    assert len(listed_bills) == initial_count
    for b in listed_bills:
        assert b.get("original_filename") != "unrelated_photo.png"
    print(" [PASS] Rejected upload is completely excluded from storage, index, and bills list.")

    # -------------------------------------------------------------
    # TEST 3: Materially incomplete or invalid extraction is rejected
    # -------------------------------------------------------------
    print("\n[TEST 3] Testing rejection of materially incomplete extraction...")
    # Has a valid provider but lacks dates, metering, and financials
    mock_incomplete_l1 = {
        "provider": "LESCO",
        "tariff": "A1",
        "sanctioned_load_kw": 2,
        "bill_month": None,
        "reading_date": None,
        "issue_date": None,
        "due_date": None,
        "previous_reading": None,
        "current_reading": None,
        "units_consumed": None,
        "charges": [],
        "total_charges": None,
        "taxes": [],
        "total_taxes": None,
        "current_bill": None,
        "arrears": None,
        "payable_within_due_date": None,
        "payable_after_due_date": None,
    }
    with patch("api.extract_bill_data", return_value=(mock_incomplete_l1, {"level1": mock_incomplete_l1})):
        res = client.post(
            "/api/bills/upload",
            files={"file": ("corrupted_bill.png", create_dummy_image(color=(10, 10, 10)), "image/png")}
        )
    assert res.status_code == 422, f"Expected 422 for incomplete bill, got {res.status_code}: {res.text}"
    print(" [PASS] Materially incomplete extraction rejected with HTTP 422.")

    # -------------------------------------------------------------
    # TEST 2: Legitimate electricity bill is accepted
    # -------------------------------------------------------------
    print("\n[TEST 2] Testing acceptance of legitimate electricity bill...")
    valid_img_bytes_1 = create_dummy_image(color=(120, 180, 220), size=(150, 150))
    mock_valid_l1_bill1 = {
        "provider": "KE",
        "tariff": "A1-R",
        "sanctioned_load_kw": 3,
        "bill_month": "2026-05",
        "reading_date": "2026-05-03",
        "issue_date": "2026-05-07",
        "due_date": "2026-05-21",
        "previous_reading": 9000,
        "current_reading": 9180,
        "units_consumed": 180,
        "charges": [{"type": "energy", "amount": 1500}],
        "total_charges": 1500,
        "taxes": [{"type": "gst", "amount": 270}],
        "total_taxes": 270,
        "current_bill": 1770,
        "arrears": 0,
        "payable_within_due_date": 1770,
        "payable_after_due_date": 1920,
    }
    mock_valid_raw_bill1 = {
        "level1": mock_valid_l1_bill1,
        "history": [{"month": "2026-04", "units": 150, "bill": 1400}],
    }

    with patch("api.extract_bill_data", return_value=(mock_valid_l1_bill1, mock_valid_raw_bill1)):
        res = client.post(
            "/api/bills/upload",
            files={"file": ("test_legit_ke.png", valid_img_bytes_1, "image/png")}
        )
    assert res.status_code == 200, f"Expected 200 for valid bill, got {res.status_code}: {res.text}"
    data_1 = res.json()
    assert data_1["success"] is True
    bill_id_1 = data_1["bill_id"]
    assert bill_id_1.startswith("bill_")
    print(f" [PASS] Legitimate bill accepted and stored with ID: {bill_id_1}")

    # -------------------------------------------------------------
    # TEST 4: Uploading the exact same image twice returns same bill ID & stores only one record
    # -------------------------------------------------------------
    print("\n[TEST 4] Testing exact duplicate upload (same bytes)...")
    index_before_dup = read_index()
    count_before_dup = len(index_before_dup)

    # This should be caught PRE-EXTRACTION without calling extract_bill_data!
    with patch("api.extract_bill_data", side_effect=Exception("Should NOT call AI on exact duplicate!")):
        res_dup = client.post(
            "/api/bills/upload",
            files={"file": ("test_legit_ke.png", valid_img_bytes_1, "image/png")}
        )
    assert res_dup.status_code == 200
    data_dup = res_dup.json()
    assert data_dup["bill_id"] == bill_id_1, f"Expected same bill_id {bill_id_1}, got {data_dup['bill_id']}"
    assert data_dup.get("duplicate") is True

    index_after_dup = read_index()
    assert len(index_after_dup) == count_before_dup, "Duplicate upload created a new index record!"
    print(f" [PASS] Exact duplicate returned existing bill ID ({bill_id_1}) without calling AI.")

    # -------------------------------------------------------------
    # TEST 5: Uploading same image under different filename or re-encoded is recognized as duplicate
    # -------------------------------------------------------------
    print("\n[TEST 5] Testing duplicate under different filename and semantic duplicate check...")
    # Subtest 5A: Same content, different filename -> caught by fast hash
    with patch("api.extract_bill_data", side_effect=Exception("Should NOT call AI on matching hash!")):
        res_alias = client.post(
            "/api/bills/upload",
            files={"file": ("renamed_statement.png", valid_img_bytes_1, "image/png")}
        )
    assert res_alias.status_code == 200
    assert res_alias.json()["bill_id"] == bill_id_1
    assert res_alias.json().get("duplicate") is True
    print(" [PASS] Same file with different filename recognized as duplicate by hash.")

    # Subtest 5B: Different image bytes (different hash) but identical unique meter readings and bill figures
    re_encoded_bytes = create_dummy_image(color=(121, 181, 221), size=(152, 152))
    with patch("api.extract_bill_data", return_value=(mock_valid_l1_bill1, mock_valid_raw_bill1)):
        res_semantic = client.post(
            "/api/bills/upload",
            files={"file": ("screenshot_copy.png", re_encoded_bytes, "image/png")}
        )
    assert res_semantic.status_code == 200
    assert res_semantic.json()["bill_id"] == bill_id_1
    assert res_semantic.json().get("duplicate") is True
    print(" [PASS] Re-encoded image with identical physical meter readings recognized as semantic duplicate.")

    # -------------------------------------------------------------
    # TEST 6: Two genuinely different bills are stored separately
    # -------------------------------------------------------------
    print("\n[TEST 6] Testing storage of genuinely different bill...")
    diff_img_bytes = create_dummy_image(color=(50, 150, 50), size=(180, 180))
    mock_valid_l1_bill2 = {
        "provider": "LESCO",
        "tariff": "A-1a(01)",
        "sanctioned_load_kw": 5,
        "bill_month": "2026-06",
        "reading_date": "2026-06-03",
        "issue_date": "2026-06-07",
        "due_date": "2026-06-21",
        "previous_reading": 1200,
        "current_reading": 1450,
        "units_consumed": 250,
        "charges": [{"type": "energy", "amount": 2500}],
        "total_charges": 2500,
        "taxes": [{"type": "gst", "amount": 450}],
        "total_taxes": 450,
        "current_bill": 2950,
        "arrears": 0,
        "payable_within_due_date": 2950,
        "payable_after_due_date": 3150,
    }
    with patch("api.extract_bill_data", return_value=(mock_valid_l1_bill2, {"level1": mock_valid_l1_bill2})):
        res_diff = client.post(
            "/api/bills/upload",
            files={"file": ("lesco_june.png", diff_img_bytes, "image/png")}
        )
    assert res_diff.status_code == 200
    data_2 = res_diff.json()
    bill_id_2 = data_2["bill_id"]
    assert bill_id_2 != bill_id_1, f"Expected distinct bill IDs, got {bill_id_1} and {bill_id_2}"
    assert data_2.get("duplicate") is False
    print(f" [PASS] Genuinely different bill stored with distinct ID ({bill_id_2}).")

    # -------------------------------------------------------------
    # TEST 8: Existing Q&A, image, detail, export endpoints verify cleanly
    # -------------------------------------------------------------
    print("\n[TEST 8] Verifying detail, image, export, and Q&A endpoints...")
    # Detail check
    det_res = client.get(f"/api/bills/{bill_id_1}")
    assert det_res.status_code == 200
    assert det_res.json()["level1"]["units_consumed"] == 180

    # Image check
    img_res = client.get(f"/api/bills/{bill_id_1}/image")
    assert img_res.status_code == 200
    assert len(img_res.content) > 0

    # Export check
    exp_res = client.get(f"/api/bills/{bill_id_1}/export")
    assert exp_res.status_code == 200
    assert exp_res.json()["provider"] == "KE"

    # QA check with mock answer
    with patch("api.answer_questions_batch", return_value={"Q1": "Total taxes are Rs. 270."}):
        qa_res = client.post(
            f"/api/bills/{bill_id_1}/ask",
            json={"question": "What are my taxes?", "question_id": "Q1"}
        )
    assert qa_res.status_code == 200
    assert "Rs. 270" in qa_res.json()["answers"]["Q1"]
    print(" [PASS] Detail, Image, Export, and Grounded Q&A endpoints verified successfully.")

    # Clean up test bills created during unit test
    api.delete_bill(bill_id_1)
    api.delete_bill(bill_id_2)

    print("\n" + "=" * 70)
    print("ALL 8 AUTOMATED TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()
