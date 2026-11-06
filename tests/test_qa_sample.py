import json
from pathlib import Path
from core.extractor import extract_bill_data
from core.qa_engine import answer_questions_batch

def main():
    img_path = Path("train/bills/KESC_0008.png")
    print(f"Extracting data for {img_path.name}...")
    level1, raw = extract_bill_data(img_path)
    history = raw.get("history", [])

    sample_questions = [
        {"question_id": "Q1", "question": "How much of my bill is taxes?"},
        {"question_id": "Q2", "question": "How many months in my history went above 200 units?"},
    ]

    print("\nAnswering sample questions...")
    answers = answer_questions_batch(img_path, level1, history, sample_questions)

    print("\n--- LEVEL 2 ANSWERS ---")
    for q in sample_questions:
        qid = q["question_id"]
        print(f"\nQuestion ({qid}): {q['question']}")
        print(f"Answer: {answers.get(qid)}")

if __name__ == "__main__":
    main()
