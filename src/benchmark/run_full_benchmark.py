import json
import time
from pathlib import Path

from model_adapter import OpenAIModel
from engine import evaluate_sql
from results_store import save_benchmark_result


BASE_DIR = Path(__file__).resolve().parents[2]
QUESTIONS_PATH = BASE_DIR / "evaluation" / "questions" / "benchmark_questions.json"
GROUND_TRUTH_PATH = BASE_DIR / "evaluation" / "ground_truth" / "ground_truth.json"
REPORT_PATH = BASE_DIR / "reports" / "full_benchmark_report.json"


def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as file:
        return json.load(file)


def main():
    questions = load_json(QUESTIONS_PATH)
    ground_truth = load_json(GROUND_TRUTH_PATH)

    model = OpenAIModel()

    total = len(questions)
    results = []

    print("\n" + "=" * 60)
    print("BENCHMARKLAB AI - FULL BENCHMARK")
    print("=" * 60)
    print(f"Model: {model.model_name}")
    print(f"Total questions: {total}")

    for index, question in enumerate(questions, start=1):
        qid = question["id"]
        dataset = question["dataset"]
        question_text = question["question"]

        print(f"\n[{index}/{total}] {qid}")
        print(f"Question: {question_text}")

        metrics = {
            "latency_ms": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

        generated_sql = ""

        try:
            model_response = model.generate_sql(
                question=question_text,
                dataset=dataset
            )

            generated_sql = model_response["sql"]
            metrics = model_response

            evaluation = evaluate_sql(
                generated_sql,
                ground_truth[qid]
            )

        except Exception as error:
            evaluation = {
                "status": "error",
                "execution_success": False,
                "result_accuracy": 0.0,
                "results_match": False,
                "error": str(error),
            }

            print(f"ERROR: {error}")

        if evaluation.get("status") == "benchmark_error":
            evaluation["execution_success"] = False
            evaluation["result_accuracy"] = 0.0

        execution_success = evaluation.get("execution_success", False)
        accuracy = evaluation.get("result_accuracy", 0.0)

        print(f"Execution success: {execution_success}")
        print(f"Accuracy: {accuracy * 100:.2f}%")
        print(f"Latency: {metrics.get('latency_ms', 0)} ms")
        print(f"Tokens: {metrics.get('total_tokens', 0)}")

        try:
            save_benchmark_result(
                model_name=model.model_name,
                question_id=qid,
                dataset=dataset,
                question=question_text,
                generated_sql=generated_sql,
                evaluation=evaluation,
                metrics=metrics
            )
            saved = True
        except Exception as storage_error:
            saved = False
            print(f"STORAGE ERROR: {storage_error}")

        results.append({
            "question_id": qid,
            "dataset": dataset,
            "question": question_text,
            "generated_sql": generated_sql,
            "evaluation": evaluation,
            "metrics": metrics,
            "saved_to_database": saved,
        })

        print(f"Saved to database: {saved}")

        # Brief pause to reduce rapid requests to the API.
        if index < total:
            time.sleep(1)

    execution_success_count = sum(
        1 for result in results
        if result["evaluation"].get("execution_success", False)
    )

    correct_count = sum(
        1 for result in results
        if result["evaluation"].get("result_accuracy", 0) == 1.0
    )

    total_latency = sum(
        result["metrics"].get("latency_ms", 0)
        for result in results
    )

    total_prompt_tokens = sum(
        result["metrics"].get("prompt_tokens", 0)
        for result in results
    )

    total_completion_tokens = sum(
        result["metrics"].get("completion_tokens", 0)
        for result in results
    )

    total_tokens = sum(
        result["metrics"].get("total_tokens", 0)
        for result in results
    )

    saved_count = sum(
        1 for result in results
        if result["saved_to_database"]
    )

    summary = {
        "model": model.model_name,
        "total_questions": total,
        "execution_success_count": execution_success_count,
        "execution_success_rate": round(
            execution_success_count / total, 4
        ) if total else 0,
        "correct_count": correct_count,
        "accuracy": round(correct_count / total, 4) if total else 0,
        "average_latency_ms": round(total_latency / total, 2) if total else 0,
        "total_latency_ms": round(total_latency, 2),
        "total_prompt_tokens": total_prompt_tokens,
        "total_completion_tokens": total_completion_tokens,
        "total_tokens": total_tokens,
        "database_saved_count": saved_count,
        "results": results,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(REPORT_PATH, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("FINAL BENCHMARK SUMMARY")
    print("=" * 60)
    print(f"Model: {model.model_name}")
    print(f"Questions: {total}")
    print(f"Execution Success: {execution_success_count}/{total}")
    print(f"Execution Success Rate: {summary['execution_success_rate'] * 100:.2f}%")
    print(f"Correct Results: {correct_count}/{total}")
    print(f"Accuracy: {summary['accuracy'] * 100:.2f}%")
    print(f"Average Latency: {summary['average_latency_ms']} ms")
    print(f"Total Prompt Tokens: {total_prompt_tokens}")
    print(f"Total Completion Tokens: {total_completion_tokens}")
    print(f"Total Tokens: {total_tokens}")
    print(f"Database Saved: {saved_count}/{total}")
    print(f"Report: {REPORT_PATH}")

    print("\nFULL BENCHMARK COMPLETED!")


if __name__ == "__main__":
    main()
