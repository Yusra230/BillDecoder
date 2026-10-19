import json
from pathlib import Path
from core.extractor import extract_bill_data

GROUND_TRUTH_KESC_0008 = {
    "provider": "KE",
    "tariff": "A1-R",
    "sanctioned_load_kw": 3,
    "bill_month": "2026-04",
    "reading_date": "2026-04-03",
    "issue_date": "2026-04-07",
    "due_date": "2026-04-21",
    "previous_reading": 8819,
    "current_reading": 8970,
    "units_consumed": 151,
    "charges": [
        {"type": "fixed", "amount": 900},
        {"type": "energy", "amount": 1054},
        {"type": "energy", "amount": 663.51},
        {"type": "quarterly_adjustment", "amount": 52.91},
        {"type": "fpa", "amount": 125.27},
        {"type": "surcharge", "amount": 64.93},
    ],
    "total_charges": 2860.62,
    "taxes": [
        {"type": "electricity_duty", "amount": 29.41},
        {"type": "gst", "amount": 520.21},
        {"type": "municipal_tax", "amount": 20},
    ],
    "total_taxes": 569.62,
    "current_bill": 3430.24,
    "arrears": -0.53,
    "payable_within_due_date": 3430,
    "payable_after_due_date": 3716,
}

def main():
    img_path = Path("train/bills/KESC_0008.png")
    print(f"Testing extraction on {img_path}...")
    level1, raw = extract_bill_data(img_path)

    print("\n--- EXTRACTED LEVEL 1 JSON ---")
    print(json.dumps(level1, indent=2))

    print("\n--- FIELD-BY-FIELD COMPARISON ---")
    discrepancies = []
    for k, expected_v in GROUND_TRUTH_KESC_0008.items():
        actual_v = level1.get(k)
        if k in ["charges", "taxes"]:
            print(f"[{k}]")
            print(f"  Expected: {expected_v}")
            print(f"  Actual:   {actual_v}")
            if expected_v != actual_v:
                discrepancies.append((k, expected_v, actual_v))
        else:
            match = (actual_v == expected_v)
            status = "MATCH" if match else "DIFF"
            print(f"[{status}] {k}: Expected={expected_v!r}, Actual={actual_v!r}")
            if not match:
                discrepancies.append((k, expected_v, actual_v))

    if not discrepancies:
        print("\n[SUCCESS] PERFECT MATCH! All fields identical to Section 5.7 ground truth.")
    else:
        print(f"\n[ALERT] Found {len(discrepancies)} discrepancies:")
        for k, exp, act in discrepancies:
            print(f"  - {k}: expected {exp}, got {act}")

if __name__ == "__main__":
    main()
