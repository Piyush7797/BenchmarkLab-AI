
from sqlalchemy import create_engine, text
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "benchmarklab.db"

engine = create_engine(f"sqlite:///{DB_PATH}")

queries = {
    "Total customers": """
        SELECT COUNT(*)
        FROM customer_shopping;
    """,

    "Average purchase amount": """
        SELECT ROUND(AVG(purchase_amount_usd), 2)
        FROM customer_shopping;
    """,

    "Category-wise customers": """
        SELECT category, COUNT(*) AS total
        FROM customer_shopping
        GROUP BY category
        ORDER BY total DESC;
    """,

    "Top 5 locations": """
        SELECT location, COUNT(*) AS customers
        FROM customer_shopping
        GROUP BY location
        ORDER BY customers DESC
        LIMIT 5;
    """
}

with engine.connect() as connection:

    for title, query in queries.items():

        print(f"\n--- {title} ---")

        result = connection.execute(text(query))

        for row in result:
            print(row)
