import json
from pathlib import Path

from engine import execute_read_only

BASE_DIR = Path(__file__).resolve().parents[2]

report_path = BASE_DIR / "reports" / "full_benchmark_report.json"
ground_truth_path = BASE_DIR / "evaluation" / "ground_truth" / "ground_truth.json"

with open(report_path, encoding="utf-8") as f:
    report = json.load(f)

with open(ground_truth_path, encoding="utf-8-sig") as f:
    ground_truth = json.load(f)

failed_ids = {"CS007", "CS008", "OR004", "OR005", "OR008"}

for result in report["results"]:
    qid = result["question_id"]

    if qid not in failed_ids:
        continue

    print("\n" + "=" * 80)
    print(f"QUESTION: {qid}")
    print(result["question"])

    predicted = execute_read_only(result["generated_sql"])
    reference = execute_read_only(ground_truth[qid])

    print("\n--- PREDICTED COLUMNS ---")
    print(predicted.get("columns"))

    print("\n--- PREDICTED ROWS ---")
    for row in predicted.get("rows", []):
        print(row)

    print("\n--- REFERENCE COLUMNS ---")
    print(reference.get("columns"))

    print("\n--- REFERENCE ROWS ---")
    for row in reference.get("rows", []):
        print(row)

