import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "benchmarklab.db"


def initialize_results_table():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS benchmark_runs (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                model_name TEXT NOT NULL,
                question_id TEXT NOT NULL,
                dataset TEXT NOT NULL,
                question TEXT NOT NULL,
                generated_sql TEXT,
                execution_success INTEGER,
                result_accuracy REAL,
                results_match INTEGER,
                latency_ms REAL,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                total_tokens INTEGER,
                evaluation_json TEXT
            )
        """)
        conn.commit()
    finally:
        conn.close()


def save_benchmark_result(
    model_name,
    question_id,
    dataset,
    question,
    generated_sql,
    evaluation,
    metrics
):
    initialize_results_table()
    conn = sqlite3.connect(DB_PATH)

    try:
        conn.execute("""
            INSERT INTO benchmark_runs (
                timestamp, model_name, question_id, dataset,
                question, generated_sql, execution_success,
                result_accuracy, results_match, latency_ms,
                prompt_tokens, completion_tokens, total_tokens,
                evaluation_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now(timezone.utc).isoformat(),
            model_name,
            question_id,
            dataset,
            question,
            generated_sql,
            int(evaluation["execution_success"]),
            evaluation["result_accuracy"],
            int(evaluation["results_match"]),
            metrics["latency_ms"],
            metrics["prompt_tokens"],
            metrics["completion_tokens"],
            metrics["total_tokens"],
            json.dumps(evaluation)
        ))
        conn.commit()
    finally:
        conn.close()


def get_benchmark_history():
    initialize_results_table()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.execute("""
            SELECT * FROM benchmark_runs
            ORDER BY run_id DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
