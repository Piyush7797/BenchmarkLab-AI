import json
from pathlib import Path

from model_adapter import OpenAIModel
from engine import evaluate_sql
from results_store import save_benchmark_result


BASE_DIR = Path(__file__).resolve().parents[2]

QUESTIONS_PATH = BASE_DIR / "evaluation" / "questions" / "benchmark_questions.json"
GROUND_TRUTH_PATH = BASE_DIR / "evaluation" / "ground_truth" / "ground_truth.json"


def main():

    with open(QUESTIONS_PATH, "r", encoding="utf-8-sig") as file:
        questions = json.load(file)

    with open(GROUND_TRUTH_PATH, "r", encoding="utf-8-sig") as file:
        ground_truth = json.load(file)

    model = OpenAIModel()

    question = questions[0]
    qid = question["id"]

    print("\n===== BENCHMARK METRICS TEST =====")
    print(f"Question ID: {qid}")
    print(f"Question: {question['question']}")
    print(f"Model: {model.model_name}")

    model_response = model.generate_sql(
        question=question["question"],
        dataset=question["dataset"]
    )

    predicted_sql = model_response["sql"]

    print("\n===== GENERATED SQL =====")
    print(predicted_sql)

    evaluation = evaluate_sql(
        predicted_sql,
        ground_truth[qid]
    )

    print("\n===== EVALUATION =====")
    print(json.dumps(evaluation, indent=2))

    print("\n===== PERFORMANCE METRICS =====")
    print(f"Latency: {model_response['latency_ms']} ms")
    print(f"Prompt Tokens: {model_response['prompt_tokens']}")
    print(f"Completion Tokens: {model_response['completion_tokens']}")
    print(f"Total Tokens: {model_response['total_tokens']}")

    save_benchmark_result(
        model_name=model.model_name,
        question_id=qid,
        dataset=question["dataset"],
        question=question["question"],
        generated_sql=predicted_sql,
        evaluation=evaluation,
        metrics=model_response
    )

    print("\n===== DATABASE STORAGE =====")
    print("Benchmark result saved to benchmarklab.db")

    print("\n===== BENCHMARK SUMMARY =====")
    print(f"Model: {model.model_name}")
    print(f"Accuracy: {evaluation['result_accuracy'] * 100:.2f}%")
    print(f"Execution Success: {evaluation['execution_success']}")
    print(f"Latency: {model_response['latency_ms']} ms")
    print(f"Total Tokens: {model_response['total_tokens']}")

    print("\nBENCHMARK RUN SAVED SUCCESSFULLY!")


if __name__ == "__main__":
    main()