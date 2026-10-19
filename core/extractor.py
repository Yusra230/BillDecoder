import json
import time
from pathlib import Path
from typing import Dict, Any, Tuple
from PIL import Image
from google import genai
from google.genai import types

from core.config import (
    MODEL_NAME,
    REQUEST_DELAY_SECONDS,
    MAX_RETRIES,
    RETRY_BACKOFF_FACTOR,
)
from core.schemas import format_bill_dict


LEVEL1_SYSTEM_INSTRUCTION = """You are an expert utility bill data extraction engine specialized in Pakistani electricity bills (K-Electric / KE, LESCO, IESCO).
Your task is to analyze the provided electricity bill image and extract billing details strictly according to the official competition schema.

EXACT OUTPUT STRUCTURE:
Return a valid JSON object with EXACTLY this structure:
{
  "level1": {
    "provider": "KE" | "LESCO" | "IESCO" | null,
    "tariff": "string or null",
    "sanctioned_load_kw": number or null,
    "bill_month": "YYYY-MM" or null,
    "reading_date": "YYYY-MM-DD" or null,
    "issue_date": "YYYY-MM-DD" or null,
    "due_date": "YYYY-MM-DD" or null,
    "previous_reading": number or null,
    "current_reading": number or null,
    "units_consumed": number or null,
    "charges": [
      {
        "type": "energy" | "fixed" | "fpa" | "quarterly_adjustment" | "surcharge" | "meter_rent" | "subsidy" | "other",
        "amount": number
      }
    ],
    "total_charges": number or null,
    "taxes": [
      {
        "type": "gst" | "electricity_duty" | "income_tax" | "municipal_tax" | "other_tax",
        "amount": number
      }
    ],
    "total_taxes": number or null,
    "current_bill": number or null,
    "arrears": number or null,
    "payable_within_due_date": number or null,
    "payable_after_due_date": number or null
  },
  "history": [
    {"month": "string", "units": number or null, "bill": number or null}
  ]
}

FIELD-SPECIFIC RULES:
- provider: Must be exactly "KE", "LESCO", or "IESCO" if this document is an electricity bill from that provider. If the document is not an electricity bill from KE, LESCO, or IESCO, set provider to null.
- tariff: The tariff code exactly as printed (e.g. "A1-R", "A-1a(01)", "A-1b(03)T", "A-2a(04)"). Look in Customer Details box under 'Tariff'.
- sanctioned_load_kw: Sanctioned load in kW, labeled 'Sanc Load', 'S.Load', or 'San Load'.
- bill_month: In YYYY-MM format (e.g. 'Apr-26' -> '2026-04', 'SEP 26' -> '2026-09', 'JUL 2026' -> '2026-07').
- reading_date, issue_date, due_date: In YYYY-MM-DD format (e.g. '03-Apr-26' -> '2026-04-03', '21st Apr 2026' -> '2026-04-21'). The due_date is the last date to pay without late surcharge.
- previous_reading, current_reading: Printed meter readings.
- units_consumed: Total units billed for the current month, as printed under Current Month / Units (KWh).
- charges: One entry per line in the charges section. Skip lines printed as 0.
  - DO NOT combine or sum lines of the same type! If the bill lists multiple lines (e.g. Variable Upto 100 Units and Variable Upto 200 Units), keep them as separate entries with type "energy".
  - type must be one of: "energy", "fixed", "fpa", "quarterly_adjustment", "surcharge", "meter_rent", "subsidy", "other". Map Quarterly Tariff Adjustment (QTR Tariff Adj, QTA) to "quarterly_adjustment".
  - If no individual charge lines are printed (e.g. LESCO bills where details are behind a covered QR code), return [].
- total_charges: Printed charges subtotal (e.g., 'Electricity Charges' subtotal or 'Total Electricity Charges'), or null if not printed.
- taxes: One entry per line in the tax or government section.
  - type must be one of: "gst", "electricity_duty", "income_tax", "municipal_tax", "other_tax".
  - If only a combined tax amount is printed, return [] and put that amount in total_taxes.
- total_taxes: Printed tax subtotal (e.g., 'Taxes and Duties' subtotal or 'Taxes'), or null if not printed.
- current_bill: Printed amount for this month's bill (e.g., 'Current Bill Amount', 'Electricity Charges for current month', or 'Current Bill').
- arrears: Previous dues carried forward. Look for 'Previous Dues' or 'Arrears'. Preserve printed sign (e.g. -0.53, or -91877.02). If blank, return null. If credit (CR), return negative number.
- payable_within_due_date: The amount payable by the due date. If credit (CR), return negative number.
- payable_after_due_date: The amount payable after the due date. If several late-payment tiers are shown, return the HIGHEST amount.
- ALL NUMERIC FIELDS must be numbers (int or float), NEVER quoted strings. Strip 'Rs.' and commas.
- SUBSIDIES & CREDITS ARE NEGATIVE: Record subsidies as negative amounts.
- EXCLUDE PII: Never return names, addresses, CNICs, account/consumer numbers, reference numbers, or meter numbers.
- UNAVAILABLE VALUES: Return null if covered or not printed. Never guess.
"""


def extract_bill_data(
    image_path: Path, client: genai.Client = None
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Extract Level 1 bill data and internal history from a bill image using gemini-3.5-flash-lite.
    Returns: (level1_clean_dict, raw_extraction_dict)
    """
    if client is None:
        client = genai.Client()

    image = Image.open(image_path)

    prompt = (
        f"Extract all billing details from this electricity bill ({image_path.name}) "
        f"strictly adhering to the rules. Return JSON with 'level1' and 'history'."
    )

    last_error = None
    delay = REQUEST_DELAY_SECONDS

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[image, prompt],
                config=types.GenerateContentConfig(
                    system_instruction=LEVEL1_SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    temperature=0.0,
                ),
            )

            raw_text = response.text.strip()
            data = json.loads(raw_text)

            level1_data = data.get("level1", data)
            # Post-process and normalize Level 1 dictionary
            level1_clean = format_bill_dict(level1_data)

            # Enforce provider constraint (do not default arbitrary filenames to KE)
            if level1_clean.get("provider") not in ["KE", "LESCO", "IESCO"]:
                fname = image_path.name.upper()
                if fname.startswith("KESC") or fname.startswith("KE_") or "K-ELECTRIC" in fname:
                    level1_clean["provider"] = "KE"
                elif fname.startswith("LESCO") or "LESCO" in fname:
                    level1_clean["provider"] = "LESCO"
                elif fname.startswith("IESCO") or "IESCO" in fname:
                    level1_clean["provider"] = "IESCO"
                else:
                    level1_clean["provider"] = None

            return level1_clean, data

        except Exception as e:
            last_error = e
            print(f"[Warning] Extraction attempt {attempt}/{MAX_RETRIES} failed for {image_path.name}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(delay)
                delay *= RETRY_BACKOFF_FACTOR

    raise RuntimeError(f"Failed to extract {image_path.name} after {MAX_RETRIES} attempts: {last_error}")
