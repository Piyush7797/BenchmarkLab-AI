
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text


# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

PROCESSED_DIR = BASE_DIR / "data" / "processed"
DB_PATH = BASE_DIR / "benchmarklab.db"

engine = create_engine(f"sqlite:///{DB_PATH}")


# ==========================================
# 2. LOAD DATASET INTO SQLITE
# ==========================================

def load_dataset(file_name, table_name):

    file_path = PROCESSED_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(file_path)

    print(f"\nLoading {file_name}...")

    df = pd.read_csv(file_path)

    print("Rows to load:", len(df))

    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=10000
    )

    print(f"Successfully loaded: {table_name}")


# ==========================================
# 3. CREATE DATABASE INDEXES
# ==========================================

def create_indexes():

    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_shopping_customer "
        "ON customer_shopping(customer_id)",

        "CREATE INDEX IF NOT EXISTS idx_retail_invoice "
        "ON online_retail(invoice_no)",

        "CREATE INDEX IF NOT EXISTS idx_retail_customer "
        "ON online_retail(customer_id)",

        "CREATE INDEX IF NOT EXISTS idx_retail_stock "
        "ON online_retail(stock_code)",

        "CREATE INDEX IF NOT EXISTS idx_retail_date "
        "ON online_retail(invoice_date)"
    ]

    with engine.begin() as connection:

        for query in indexes:
            connection.execute(text(query))

    print("\nDatabase indexes created successfully!")


# ==========================================
# 4. VERIFY DATABASE
# ==========================================

def verify_database():

    tables = [
        "customer_shopping",
        "online_retail"
    ]

    print("\nDATABASE VERIFICATION")
    print("=" * 40)

    with engine.connect() as connection:

        for table in tables:

            result = connection.execute(
                text(f"SELECT COUNT(*) FROM {table}")
            )

            count = result.scalar()

            print(f"{table}: {count:,} rows")


# ==========================================
# 5. MAIN EXECUTION
# ==========================================

def main():

    print("\nBENCHMARKLAB AI - DATABASE LOADER")

    load_dataset(
        "customer_shopping_clean.csv",
        "customer_shopping"
    )

    load_dataset(
        "online_retail_clean.csv",
        "online_retail"
    )

    create_indexes()

    verify_database()

    print("\nDATABASE LOADING COMPLETED!")


if __name__ == "__main__":
    main()
