import csv
import json
from pathlib import Path
from typing import List, Dict, Any


def write_level1_csv(output_path: Path, rows: List[Dict[str, Any]]):
    """
    Writes level1.csv.
    rows: list of dicts: {"bill_id": str, "json": dict_or_json_str}
    Requirement:
    - columns: bill_id, json
    - each JSON object on a single line
    - inside quoted CSV cell, quotes doubled (standard CSV behavior)
    - UTF-8 encoding
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["bill_id", "json"])
        for r in rows:
            bill_id = r["bill_id"]
            json_val = r["json"]
            if isinstance(json_val, dict):
                # Compact single-line JSON
                json_str = json.dumps(json_val, separators=(",", ":"), ensure_ascii=False)
            else:
                json_str = str(json_val).replace("\r", "").replace("\n", " ").strip()
            writer.writerow([bill_id, json_str])


def write_level2_csv(output_path: Path, rows: List[Dict[str, str]]):
    """
    Writes level2.csv.
    rows: list of dicts: {"bill_id": str, "question_id": str, "question": str, "answer": str}
    Requirement:
    - columns: bill_id, question_id, question, answer
    - preserved row order
    - UTF-8 encoding
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["bill_id", "question_id", "question", "answer"],
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()
        for r in rows:
            # Clean newlines from answer to ensure clean CSV row structure
            ans_clean = str(r.get("answer", "")).replace("\r", " ").replace("\n", " ").strip()
            writer.writerow({
                "bill_id": r["bill_id"],
                "question_id": r["question_id"],
                "question": r["question"],
                "answer": ans_clean,
            })
