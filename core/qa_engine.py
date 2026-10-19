import json
import time
from pathlib import Path
from typing import Dict, List, Any
from PIL import Image
from google import genai
from google.genai import types

from core.config import (
    MODEL_NAME,
    REQUEST_DELAY_SECONDS,
    MAX_RETRIES,
    RETRY_BACKOFF_FACTOR,
)


LEVEL2_SYSTEM_INSTRUCTION = """You are an expert customer assistant for Pakistani electricity bills (KE, LESCO, IESCO).
Your task is to answer customer questions about the bill in plain English, strictly grounded in the bill.

CRITICAL RULES:
1. GET THE NUMBERS RIGHT: Exact figures, differences, percentages, averages, and counts are strictly checked.
2. GROUND EACH ANSWER IN THE BILL: Rely ONLY on facts visible on the bill image or provided extracted data. Do NOT use external tariff knowledge or outside assumptions. If the bill does not show a needed value, say clearly that the information is not shown or not available on the bill, instead of guessing.
3. LABEL ESTIMATES: If an answer requires an estimate or projection (e.g. expected next month units, spreading costs, future bills), explicitly state that it is an estimate and explain how it was calculated.
4. EXPLAIN AMBIGUOUS INTERPRETATIONS: If a question has more than one reasonable interpretation, state the interpretation used or address both.
5. EXCLUDE PERSONAL IDENTIFIERS: Never reveal consumer name, address, CNIC, account number, consumer number, reference number, or meter number.
6. ANSWER IN ENGLISH: Always write answers in clear, polite English, even if sections of the bill are in Urdu.
7. DETAILED GUIDANCE FOR SPECIFIC QUESTIONS:
   - Net-metered vs standard: State clearly whether it is a net-metered (solar) or standard connection, and explain how you told (e.g., presence of Peak/Off-Peak and Import/Export readings, "NET METERING CONNECTION" text, negative credit balance, vs standard single-phase unidirectional meter).
   - Highest units consumed in last 12 months: State the specific month and unit count from the usage history table/chart.
   - FPA / FCA charges: State the exact amount in PKR and the specific month it applies to (from the charges breakdown table or message board/Urdu note).
   - Late payment surcharges: State the surcharge amount (the difference between payable after due date and payable within due date, or the printed L.P Surcharge).
   - Consuming more units than same month last year: State the current month units and the units from the same month last year in the history table, and state whether it increased or decreased.
   - Average monthly units consumed: Calculate the average monthly units from the 12-month history, and compare the current month to that average.
   - Summer (June-August) vs Winter (December-February): Sum the units for June, July, August and sum the units for December, January, February from the history, and state the difference. If some months are missing, state the available months.
   - Payments over 12 months: Look at the Payment column in the history table. State whether all bills were paid, or identify any months with 0 or missing payments.
   - Trend over last 3 months: State whether consumption went up or down across the most recent 3 months, listing the units for each month.
   - Expected units next month: Provide an estimate (e.g. based on the same month last year or recent trend), explicitly label it as an estimate, and explain the calculation basis.
   - Spreading cost evenly across the year: Provide an estimated monthly amount based on the average monthly bill from the 12-month history (total billed / 12), explicitly label as an estimate.
   - Rough bill if same units as last month: Estimate the bill amount based on last month's bill, explicitly label as an estimate, and explain the basis.

RESPONSE FORMAT:
Return a JSON object with an "answers" dictionary mapping each question_id to its final plain English answer string:
{
  "answers": {
    "Q1": "answer text",
    "Q2": "answer text"
  }
}
"""


def answer_questions_batch(
    image_path: Path,
    level1_data: Dict[str, Any],
    history_data: List[Dict[str, Any]],
    questions: List[Dict[str, str]],
    client: genai.Client = None,
) -> Dict[str, str]:
    """
    Answers a list of questions for a bill in a single API call.
    questions: list of {"question_id": "Q1", "question": "..."}
    Returns: dict mapping question_id -> answer_string
    """
    if client is None:
        client = genai.Client()

    image = Image.open(image_path)

    # Compute helper summary metrics with Python
    helpers = []
    if level1_data.get("current_bill") and level1_data.get("total_taxes"):
        cb = float(level1_data["current_bill"])
        tt = float(level1_data["total_taxes"])
        if cb > 0:
            tax_pct = (tt / cb) * 100
            helpers.append(f"Computed tax percentage: {tax_pct:.2f}% of current bill ({tt} / {cb})")

    context_str = json.dumps({
        "bill_id": image_path.stem,
        "extracted_level1": level1_data,
        "extracted_history": history_data,
        "python_calculations": helpers,
    }, indent=2)

    prompt = (
        f"Bill ID: {image_path.stem}\n"
        f"Bill Data Context:\n{context_str}\n\n"
        f"Questions to answer:\n{json.dumps(questions, indent=2)}\n\n"
        f"Answer each question accurately and return the JSON object with the 'answers' map."
    )

    last_error = None
    delay = REQUEST_DELAY_SECONDS

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[image, prompt],
                config=types.GenerateContentConfig(
                    system_instruction=LEVEL2_SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    temperature=0.0,
                ),
            )

            res = json.loads(response.text.strip())
            answers_dict = res.get("answers", res)

            # Ensure every question_id has an answer string
            out_answers = {}
            for q in questions:
                qid = q["question_id"]
                ans = answers_dict.get(qid)
                if not ans:
                    # Fallback if key missing
                    ans = f"Information for {q['question']} is not available on the bill."
                out_answers[qid] = str(ans).strip()

            return out_answers

        except Exception as e:
            last_error = e
            print(f"[Warning] Level 2 QA attempt {attempt}/{MAX_RETRIES} failed for {image_path.name}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(delay)
                delay *= RETRY_BACKOFF_FACTOR

    raise RuntimeError(f"Failed to answer questions for {image_path.name}: {last_error}")
