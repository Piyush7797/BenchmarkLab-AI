import json
from pathlib import Path

from engine import evaluate_sql
from semantic_engine import evaluate_sql_semantic

BASE_DIR = Path(__file__).resolve().parents[2]

REPORT_PATH = BASE_DIR / "reports" / "full_benchmark_report.json"
GROUND_TRUTH_PATH = BASE_DIR / "evaluation" / "ground_truth" / "ground_truth.json"
OUTPUT_PATH = BASE_DIR / "reports" / "semantic_benchmark_report.json"

with open(REPORT_PATH, encoding="utf-8") as f:
    report = json.load(f)

with open(GROUND_TRUTH_PATH, encoding="utf-8-sig") as f:
    ground_truth = json.load(f)

results = []

for item in report["results"]:
    qid = item["question_id"]
    predicted_sql = item["generated_sql"]
    reference_sql = ground_truth[qid]

    strict = evaluate_sql(predicted_sql, reference_sql)
    semantic = evaluate_sql_semantic(predicted_sql, reference_sql)

    results.append({
        "question_id": qid,
        "strict_accuracy": strict.get("result_accuracy", 0),
        "strict_execution_success": strict.get("execution_success", False),
        "semantic_accuracy": semantic.get("result_accuracy", 0),
        "semantic_execution_success": semantic.get("execution_success", False),
        "semantic_match": semantic.get("results_match", False),
    })

total = len(results)

strict_correct = sum(r["strict_accuracy"] == 1.0 for r in results)
semantic_correct = sum(r["semantic_accuracy"] == 1.0 for r in results)

strict_execution = sum(r["strict_execution_success"] for r in results)
semantic_execution = sum(r["semantic_execution_success"] for r in results)

report_v2 = {
    "total_questions": total,
    "strict_accuracy": strict_correct / total if total else 0,
    "semantic_accuracy": semantic_correct / total if total else 0,
    "strict_execution_success_rate": strict_execution / total if total else 0,
    "semantic_execution_success_rate": semantic_execution / total if total else 0,
    "strict_correct": strict_correct,
    "semantic_correct": semantic_correct,
    "results": results,
}

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(report_v2, f, indent=4)

print("\n===== FULL BENCHMARK EVALUATION V2 =====")
print(f"Total Questions: {total}")
print(f"Strict Accuracy: {strict_correct}/{total} ({strict_correct / total * 100:.2f}%)")
print(f"Semantic Accuracy: {semantic_correct}/{total} ({semantic_correct / total * 100:.2f}%)")
print(f"Strict Execution: {strict_execution}/{total} ({strict_execution / total * 100:.2f}%)")
print(f"Semantic Execution: {semantic_execution}/{total} ({semantic_execution / total * 100:.2f}%)")

print("\n===== QUESTION RESULTS =====")

for r in results:
    strict_status = "PASS" if r["strict_accuracy"] == 1.0 else "FAIL"
    semantic_status = "PASS" if r["semantic_accuracy"] == 1.0 else "FAIL"

    print(
        f'{r["question_id"]}: '
        f'Strict={strict_status} | Semantic={semantic_status}'
    )

print(f"\nReport saved: {OUTPUT_PATH}")
