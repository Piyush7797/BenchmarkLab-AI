import json
from pathlib import Path

from semantic_engine import evaluate_sql_semantic

BASE_DIR = Path(__file__).resolve().parents[2]

REPORT_PATH = BASE_DIR / "reports" / "full_benchmark_report.json"
GROUND_TRUTH_PATH = BASE_DIR / "evaluation" / "ground_truth" / "ground_truth.json"

with open(REPORT_PATH, encoding="utf-8") as f:
    report = json.load(f)

with open(GROUND_TRUTH_PATH, encoding="utf-8-sig") as f:
    ground_truth = json.load(f)

failed_ids = {"CS007", "CS008", "OR004", "OR005", "OR008"}

results = []

print("\n===== SEMANTIC EVALUATOR V2 TEST =====")

for result in report["results"]:
    qid = result["question_id"]

    if qid not in failed_ids:
        continue

    evaluation = evaluate_sql_semantic(
        result["generated_sql"],
        ground_truth[qid]
    )

    results.append((qid, evaluation))

    print(f"\nQuestion: {qid}")
    print(f"Status: {evaluation.get('status')}")
    print(f"Execution Success: {evaluation.get('execution_success')}")
    print(f"Semantic Match: {evaluation.get('results_match')}")
    print(f"Accuracy: {evaluation.get('result_accuracy')}")

print("\n===== SUMMARY =====")

semantic_passes = sum(
    evaluation.get("result_accuracy", 0) == 1.0
    for _, evaluation in results
)

print(f"Tested: {len(results)}")
print(f"Semantic matches: {semantic_passes}")
print(f"Semantic mismatches: {len(results) - semantic_passes}")

for qid, evaluation in results:
    print(
        f"{qid}: "
        f"{'PASS' if evaluation.get('result_accuracy') == 1.0 else 'FAIL'}"
    )
