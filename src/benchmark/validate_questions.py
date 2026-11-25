import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

QUESTIONS_FILE = BASE_DIR / "evaluation" / "questions" / "benchmark_questions.json"
GROUND_TRUTH_FILE = BASE_DIR / "evaluation" / "ground_truth" / "ground_truth.json"
DATABASE_FILE = BASE_DIR / "benchmarklab.db"


def main():
    for file in [QUESTIONS_FILE, GROUND_TRUTH_FILE, DATABASE_FILE]:
        if not file.exists():
            print(f"MISSING FILE: {file}")
            return

    with open(QUESTIONS_FILE, encoding="utf-8-sig") as f:
        questions = json.load(f)

    with open(GROUND_TRUTH_FILE, encoding="utf-8-sig") as f:
        ground_truth = json.load(f)

    ids = [q["id"] for q in questions]

    if len(ids) != len(set(ids)):
        print("ERROR: Duplicate question IDs!")
        return

    if set(ids) != set(ground_truth.keys()):
        print("ERROR: Question IDs do not match ground truth SQL IDs!")
        return

    conn = sqlite3.connect(f"file:{DATABASE_FILE}?mode=ro", uri=True)
    conn.execute("PRAGMA query_only = ON")

    passed = 0
    failed = 0

    print("\n===== BENCHMARK VALIDATION =====\n")

    for question in questions:
        qid = question["id"]

        try:
            result = conn.execute(ground_truth[qid])
            rows = result.fetchall()

            print(f"PASS | {qid} | {len(rows)} rows")
            passed += 1

        except Exception as error:
            print(f"FAIL | {qid} | {error}")
            failed += 1

    conn.close()

    print("\n===== SUMMARY =====")
    print(f"Total: {len(questions)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
