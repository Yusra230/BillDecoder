import json
import time
from pathlib import Path
from core.extractor import extract_bill_data
from core.config import TRAIN_BILLS_DIR, REQUEST_DELAY_SECONDS

def main():
    bills = sorted(list(TRAIN_BILLS_DIR.glob("*.*")))
    print(f"Found {len(bills)} training bills: {[b.name for b in bills]}")

    results = {}
    for i, bill_path in enumerate(bills, 1):
        print(f"\n[{i}/{len(bills)}] Extracting {bill_path.name}...")
        try:
            level1, raw = extract_bill_data(bill_path)
            results[bill_path.name] = level1
            print(f"Extracted successfully: Provider={level1.get('provider')}, Units={level1.get('units_consumed')}, Month={level1.get('bill_month')}, Due={level1.get('due_date')}")
            print(f"  Charges count: {len(level1.get('charges', []))}, Taxes count: {len(level1.get('taxes', []))}")
            print(f"  Total Charges: {level1.get('total_charges')}, Total Taxes: {level1.get('total_taxes')}")
            print(f"  Arrears: {level1.get('arrears')}, Payable: {level1.get('payable_within_due_date')}")
        except Exception as e:
            print(f"ERROR extracting {bill_path.name}: {e}")

        if i < len(bills):
            print(f"Pacing delay: sleeping {REQUEST_DELAY_SECONDS}s...")
            time.sleep(REQUEST_DELAY_SECONDS)

    print("\n" + "="*50)
    print("ALL 5 BILLS SUMMARY:")
    print("="*50)
    for name, data in results.items():
        print(f"\n--- {name} ---")
        print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()
