import csv
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple


REQUIRED_L1_KEYS = [
    "provider",
    "tariff",
    "sanctioned_load_kw",
    "bill_month",
    "reading_date",
    "issue_date",
    "due_date",
    "previous_reading",
    "current_reading",
    "units_consumed",
    "charges",
    "total_charges",
    "taxes",
    "total_taxes",
    "current_bill",
    "arrears",
    "payable_within_due_date",
    "payable_after_due_date",
]

ALLOWED_PROVIDERS = {"KE", "LESCO", "IESCO"}
ALLOWED_CHARGE_TYPES = {
    "energy",
    "fixed",
    "fpa",
    "quarterly_adjustment",
    "surcharge",
    "meter_rent",
    "subsidy",
    "other",
}
ALLOWED_TAX_TYPES = {
    "gst",
    "electricity_duty",
    "income_tax",
    "municipal_tax",
    "other_tax",
}


def validate_level1_csv(file_path: Path, expected_rows: int = None) -> Tuple[bool, List[str]]:
    errors = []
    if not file_path.exists():
        return False, [f"File does not exist: {file_path}"]

    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header != ["bill_id", "json"]:
            errors.append(f"Invalid level1.csv header: {header}. Expected ['bill_id', 'json']")

        rows = list(reader)

    if expected_rows is not None and len(rows) != expected_rows:
        errors.append(f"Row count mismatch: got {len(rows)}, expected {expected_rows}")

    for idx, row in enumerate(rows, 1):
        if len(row) != 2:
            errors.append(f"Row {idx} has {len(row)} columns, expected 2")
            continue
        bill_id, json_str = row[0], row[1]
        if not bill_id.strip():
            errors.append(f"Row {idx}: bill_id is empty")

        try:
            data = json.loads(json_str)
        except Exception as e:
            errors.append(f"Row {idx} ({bill_id}): invalid JSON string ({e})")
            continue

        if not isinstance(data, dict):
            errors.append(f"Row {idx} ({bill_id}): JSON is not an object")
            continue

        for k in REQUIRED_L1_KEYS:
            if k not in data:
                errors.append(f"Row {idx} ({bill_id}): missing required key '{k}'")

        prov = data.get("provider")
        if prov not in ALLOWED_PROVIDERS:
            errors.append(f"Row {idx} ({bill_id}): invalid provider '{prov}'. Must be KE, LESCO, or IESCO")

        # Check charges
        charges = data.get("charges")
        if not isinstance(charges, list):
            errors.append(f"Row {idx} ({bill_id}): 'charges' must be a list")
        else:
            for c_idx, c in enumerate(charges):
                if not isinstance(c, dict):
                    errors.append(f"Row {idx} ({bill_id}): charge {c_idx} is not an object")
                elif c.get("type") not in ALLOWED_CHARGE_TYPES:
                    errors.append(f"Row {idx} ({bill_id}): charge {c_idx} invalid type '{c.get('type')}'")

        # Check taxes
        taxes = data.get("taxes")
        if not isinstance(taxes, list):
            errors.append(f"Row {idx} ({bill_id}): 'taxes' must be a list")
        else:
            for t_idx, t in enumerate(taxes):
                if not isinstance(t, dict):
                    errors.append(f"Row {idx} ({bill_id}): tax {t_idx} is not an object")
                elif t.get("type") not in ALLOWED_TAX_TYPES:
                    errors.append(f"Row {idx} ({bill_id}): tax {t_idx} invalid type '{t.get('type')}'")

        # Check numeric types
        numeric_fields = [
            "sanctioned_load_kw",
            "previous_reading",
            "current_reading",
            "units_consumed",
            "total_charges",
            "total_taxes",
            "current_bill",
            "arrears",
            "payable_within_due_date",
            "payable_after_due_date",
        ]
        for nf in numeric_fields:
            v = data.get(nf)
            if v is not None and not isinstance(v, (int, float)):
                errors.append(f"Row {idx} ({bill_id}): field '{nf}' must be numeric or null, got {type(v).__name__}: {v!r}")

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_level2_csv(file_path: Path, expected_rows: int = None) -> Tuple[bool, List[str]]:
    errors = []
    if not file_path.exists():
        return False, [f"File does not exist: {file_path}"]

    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header != ["bill_id", "question_id", "question", "answer"]:
            errors.append(f"Invalid level2.csv header: {header}. Expected ['bill_id', 'question_id', 'question', 'answer']")

        rows = list(reader)

    if expected_rows is not None and len(rows) != expected_rows:
        errors.append(f"Row count mismatch: got {len(rows)}, expected {expected_rows}")

    for idx, row in enumerate(rows, 1):
        if len(row) != 4:
            errors.append(f"Row {idx} has {len(row)} columns, expected 4")
            continue
        bill_id, qid, question, answer = row[0], row[1], row[2], row[3]
        if not bill_id.strip():
            errors.append(f"Row {idx}: bill_id is empty")
        if not qid.strip():
            errors.append(f"Row {idx}: question_id is empty")
        if not question.strip():
            errors.append(f"Row {idx}: question is empty")
        if not answer.strip():
            errors.append(f"Row {idx} ({bill_id}, {qid}): answer is EMPTY!")

    is_valid = len(errors) == 0
    return is_valid, errors
