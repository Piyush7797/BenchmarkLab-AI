import re
from collections import Counter
from decimal import Decimal, InvalidOperation


def normalize_text(value):
    if not isinstance(value, str):
        return value

    text = value.strip().lower()

    # Normalize age-band labels
    age_labels = {
        "under 25": "under 25",
        "25 to 44": "25-44",
        "25-44": "25-44",
        "45 to 59": "45-59",
        "45-59": "45-59",
        "60 or above": "60+",
        "60+": "60+",
    }

    if text in age_labels:
        return age_labels[text]

    # Normalize YYYY-MM month labels
    if re.fullmatch(r"\d{4}-\d{1,2}", text):
        year, month = text.split("-")
        return f"{year}-{int(month):02d}"

    return text


def normalize_row(row):
    row = list(row)

    # Normalize year/month columns:
    # (2011, 1, 100.0) -> ("2011-01", 100.0)
    if (
        len(row) >= 2
        and isinstance(row[0], int)
        and isinstance(row[1], int)
        and 1 <= row[1] <= 12
        and 1900 <= row[0] <= 2100
    ):
        row = [f"{row[0]}-{row[1]:02d}"] + row[2:]

    return tuple(normalize_text(value) for value in row)


def values_equal(a, b, tolerance=1e-6):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) <= tolerance

    # Numeric values stored in different representations
    if isinstance(a, str) and isinstance(b, str):
        try:
            da = Decimal(a)
            db = Decimal(b)
            return abs(da - db) <= Decimal(str(tolerance))
        except (InvalidOperation, ValueError):
            pass

    return a == b


def rows_equal(predicted_rows, reference_rows, tolerance=1e-6):
    if len(predicted_rows) != len(reference_rows):
        return False

    predicted = [normalize_row(row) for row in predicted_rows]
    reference = [normalize_row(row) for row in reference_rows]

    # Ignore row ordering; preserve duplicate rows.
    unmatched = list(reference)

    for predicted_row in predicted:
        match_index = None

        for index, reference_row in enumerate(unmatched):
            if len(predicted_row) != len(reference_row):
                continue

            if all(
                values_equal(p, r, tolerance)
                for p, r in zip(predicted_row, reference_row)
            ):
                match_index = index
                break

        if match_index is None:
            return False

        unmatched.pop(match_index)

    return not unmatched


def evaluate_sql_semantic(predicted_sql, reference_sql):
    # Import the existing safe execution engine
    from engine import execute_read_only

    predicted_result = execute_read_only(predicted_sql)
    reference_result = execute_read_only(reference_sql)

    if not reference_result["success"]:
        return {
            "status": "benchmark_error",
            "error": reference_result.get("error"),
        }

    if not predicted_result["success"]:
        return {
            "status": "execution_error",
            "execution_success": False,
            "result_accuracy": 0.0,
            "error": predicted_result.get("error"),
        }

    predicted_rows = predicted_result["rows"]
    reference_rows = reference_result["rows"]

    match = rows_equal(predicted_rows, reference_rows)

    return {
        "status": "success",
        "execution_success": True,
        "result_accuracy": 1.0 if match else 0.0,
        "results_match": match,
        "comparison_method": "semantic_v2",
        "predicted_row_count": len(predicted_rows),
        "reference_row_count": len(reference_rows),
        "predicted_columns": predicted_result["columns"],
        "reference_columns": reference_result["columns"],
    }
