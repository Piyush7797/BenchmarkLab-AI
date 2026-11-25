import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "benchmarklab.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM benchmark_runs")
        total = cursor.fetchone()[0]

        print("\n===== BENCHMARK HISTORY =====")
        print(f"Total saved runs: {total}\n")

        cursor.execute("""
            SELECT
                run_id,
                timestamp,
                model_name,
                question_id,
                execution_success,
                result_accuracy,
                latency_ms,
                total_tokens
            FROM benchmark_runs
            ORDER BY run_id DESC
        """)

        rows = cursor.fetchall()

        for row in rows:
            print("-" * 60)
            print(f"Run ID: {row[0]}")
            print(f"Timestamp: {row[1]}")
            print(f"Model: {row[2]}")
            print(f"Question: {row[3]}")
            print(f"Execution Success: {row[4]}")
            print(f"Accuracy: {row[5]}")
            print(f"Latency: {row[6]} ms")
            print(f"Total Tokens: {row[7]}")

    finally:
        conn.close()

if __name__ == "__main__":
    main()
