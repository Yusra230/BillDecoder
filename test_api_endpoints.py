import sys
import json
from pathlib import Path
from fastapi.testclient import TestClient

from api import app, UPLOADS_DIR

client = TestClient(app)

def run_tests():
    print("=" * 60)
    print("STAGE 1: BACKEND HEALTH & ROUTING CHECKS")
    print("=" * 60)

    # 1. Health check
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health_data = res.json()
    assert health_data["status"] == "healthy"
    print(f" [PASS] GET /api/health -> {health_data}")

    # 2. List bills (initially empty or existing)
    res = client.get("/api/bills")
    assert res.status_code == 200, f"List bills failed: {res.text}"
    bills_list = res.json()
    assert isinstance(bills_list, list)
    print(f" [PASS] GET /api/bills -> currently {len(bills_list)} bills in index.")

    # 3. Test Static index.html serving
    res = client.get("/")
    assert res.status_code == 200
    assert "VoltDecoder" in res.text or "<div id=\"root\">" in res.text
    print(f" [PASS] GET / -> Successfully serves compiled React index.html")

    # 4. Upload & Extract test with a real bill image
    sample_bill_path = Path("train/bills/KESC_0008.png")
    if not sample_bill_path.exists():
        print(f" [SKIP] Sample bill {sample_bill_path} not found for live extraction.")
        return

    print("\n" + "=" * 60)
    print("STAGE 2: END-TO-END UPLOAD & LIVE AI EXTRACTION TEST")
    print("=" * 60)
    print(f"Uploading {sample_bill_path.name} to /api/bills/upload...")

    with open(sample_bill_path, "rb") as f:
        res = client.post(
            "/api/bills/upload",
            files={"file": ("KESC_0008.png", f, "image/png")}
        )

    assert res.status_code == 200, f"Upload failed: {res.text}"
    upload_res = res.json()
    assert upload_res["success"] is True
    bill_id = upload_res["bill_id"]
    l1 = upload_res["level1"]
    hist = upload_res["history"]

    print(f" [PASS] Extracted {bill_id}:")
    print(f"        Provider: {l1.get('provider')}")
    print(f"        Month: {l1.get('bill_month')}")
    print(f"        Units: {l1.get('units_consumed')}")
    print(f"        Payable within due: Rs. {l1.get('payable_within_due_date')}")
    print(f"        History months extracted: {len(hist)}")

    # 5. Detail inspection
    res = client.get(f"/api/bills/{bill_id}")
    assert res.status_code == 200
    detail = res.json()
    assert detail["metadata"]["bill_id"] == bill_id
    assert detail["level1"]["provider"] == l1["provider"]
    print(f" [PASS] GET /api/bills/{bill_id} -> verified detail matches extracted data.")

    # 6. Image retrieval
    res = client.get(f"/api/bills/{bill_id}/image")
    assert res.status_code == 200
    assert res.headers["content-type"] in ["image/png", "image/jpeg"]
    assert len(res.content) > 1000
    print(f" [PASS] GET /api/bills/{bill_id}/image -> served {len(res.content)} bytes.")

    # 7. Grounded QA query test
    print("\n" + "=" * 60)
    print("STAGE 3: GROUNDED QUESTION-ANSWERING (LEVEL 2) TEST")
    print("=" * 60)
    test_question = "How much of my bill is taxes?"
    print(f"Asking question: '{test_question}'...")

    res = client.post(
        f"/api/bills/{bill_id}/ask",
        json={"question": test_question, "question_id": "Q1"}
    )
    assert res.status_code == 200, f"QA query failed: {res.text}"
    qa_res = res.json()
    assert qa_res["success"] is True
    answer = qa_res["answers"].get("Q1")
    assert answer and len(answer) > 5
    print(f" [PASS] Answer received for Q1:")
    print(f"        \"{answer}\"")

    # 8. Export check
    res = client.get(f"/api/bills/{bill_id}/export")
    assert res.status_code == 200
    exported_data = res.json()
    assert exported_data.get("provider") == l1.get("provider")
    print(f" [PASS] GET /api/bills/{bill_id}/export -> verified valid exported Level 1 JSON.")

    print("\n" + "=" * 60)
    print("ALL API END-TO-END VERIFICATION CHECKS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
