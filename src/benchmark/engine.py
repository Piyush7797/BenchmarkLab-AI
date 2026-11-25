import sqlite3
import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_FILE = BASE_DIR / "benchmarklab.db"


def normalize_rows(rows):
    normalized = [
        json.dumps(list(row), sort_keys=True, default=str)
        for row in rows
    ]
    return Counter(normalized)


def safe_authorizer(action, arg1, arg2, database, trigger):
    allowed_actions = {
        sqlite3.SQLITE_SELECT,
        sqlite3.SQLITE_READ,
        sqlite3.SQLITE_FUNCTION,
    }

    if hasattr(sqlite3, "SQLITE_RECURSIVE"):
        allowed_actions.add(sqlite3.SQLITE_RECURSIVE)

    if action in allowed_actions:
        return sqlite3.SQLITE_OK

    return sqlite3.SQLITE_DENY


def execute_read_only(sql):
    conn = sqlite3.connect(
        f"file:{DATABASE_FILE}?mode=ro",
        uri=True
    )

    try:
        conn.execute("PRAGMA query_only = ON")
        conn.set_authorizer(safe_authorizer)

        cursor = conn.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []

        return {
            "success": True,
            "rows": rows,
            "columns": columns
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
            "rows": [],
            "columns": []
        }

    finally:
        conn.close()


def evaluate_sql(predicted_sql, reference_sql):
    predicted_result = execute_read_only(predicted_sql)
    reference_result = execute_read_only(reference_sql)

    if not reference_result["success"]:
        return {
            "status": "benchmark_error",
            "error": reference_result["error"]
        }

    if not predicted_result["success"]:
        return {
            "status": "execution_error",
            "error": predicted_result["error"],
            "execution_success": False,
            "result_accuracy": 0.0
        }

    predicted_rows = predicted_result["rows"]
    reference_rows = reference_result["rows"]

    results_match = (
        normalize_rows(predicted_rows)
        == normalize_rows(reference_rows)
    )

    return {
        "status": "success",
        "execution_success": True,
        "result_accuracy": 1.0 if results_match else 0.0,
        "results_match": results_match,
        "predicted_row_count": len(predicted_rows),
        "reference_row_count": len(reference_rows),
        "predicted_columns": predicted_result["columns"],
        "reference_columns": reference_result["columns"]
    }
