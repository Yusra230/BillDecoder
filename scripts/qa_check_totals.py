import csv
import json
from pathlib import Path

def main():
    rows = list(csv.reader(open("output/level1.csv", encoding="utf-8")))[1:]
    for r in rows:
        bid = r[0]
        data = json.loads(r[1])
        tc = data.get("total_charges")
        sum_c = sum(c.get("amount", 0) for c in data.get("charges", []))
        tt = data.get("total_taxes")
        sum_t = sum(t.get("amount", 0) for t in data.get("taxes", []))
        cb = data.get("current_bill")
        arr = data.get("arrears")
        pwd = data.get("payable_within_due_date")
        pad = data.get("payable_after_due_date")

        print(f"\n[{bid}]")
        print(f"  total_charges: {tc} | sum(charges): {sum_c:.2f} (count={len(data.get('charges', []))})")
        print(f"  total_taxes:   {tt} | sum(taxes):   {sum_t:.2f} (count={len(data.get('taxes', []))})")
        print(f"  current_bill:  {cb} | arrears: {arr} | payable_within: {pwd} | payable_after: {pad}")

if __name__ == "__main__":
    main()
