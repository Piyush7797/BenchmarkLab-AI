import json
from pathlib import Path
from engine import evaluate_sql

BASE_DIR = Path(__file__).resolve().parents[2]

QUESTIONS_FILE = BASE_DIR / "evaluation" / "questions" / "benchmark_questions.json"
GROUND_TRUTH_FILE = BASE_DIR / "evaluation" / "ground_truth" / "ground_truth.json"


def main():
    with open(QUESTIONS_FILE, encoding="utf-8-sig") as f:
        questions = json.load(f)

    with open(GROUND_TRUTH_FILE, encoding="utf-8-sig") as f:
        ground_truth = json.load(f)

    passed = 0
    failed = 0

    print("\n===== BENCHMARK ENGINE TEST =====\n")

    for question in questions:
        qid = question["id"]
        reference_sql = ground_truth[qid]

        result = evaluate_sql(reference_sql, reference_sql)

        if result.get("results_match") is True:
            print(f"PASS | {qid} | Accuracy: 100%")
            passed += 1
        else:
            print(f"FAIL | {qid} | {result}")
            failed += 1

    print("\n===== ENGINE TEST SUMMARY =====")
    print(f"Total: {len(questions)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if passed == len(questions):
        print("\nBENCHMARK ENGINE TEST SUCCESSFUL!")


if __name__ == "__main__":
    main()
