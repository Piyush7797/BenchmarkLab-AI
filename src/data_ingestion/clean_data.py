
import pandas as pd
import re
from pathlib import Path


# ==================================================
# 1. PROJECT CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# 2. STANDARDIZE COLUMN NAMES
# ==================================================

def standardize_columns(df):

    df.columns = [
        re.sub(
            r"[^a-zA-Z0-9]+",
            "_",
            re.sub(
                r"([a-z0-9])([A-Z])",
                r"\1_\2",
                str(col).strip()
            )
        ).strip("_").lower()
        for col in df.columns
    ]

    return df


# ==================================================
# 3. CLEAN CUSTOMER SHOPPING DATA
# ==================================================

def clean_shopping_data():

    print("\n" + "=" * 50)
    print("CUSTOMER SHOPPING DATA CLEANING")
    print("=" * 50)

    path = RAW_DIR / "customer_shopping_behavior.csv"

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)

    print("Original shape:", df.shape)

    # Standardize column names
    df = standardize_columns(df)

    # Remove exact duplicates
    initial_rows = len(df)
    df = df.drop_duplicates()
    removed_duplicates = initial_rows - len(df)

    # Clean text columns
    for col in df.select_dtypes(include=["object", "str"]):
        df[col] = df[col].str.strip()

    # Validate required columns
    required_columns = [
        "customer_id",
        "age",
        "purchase_amount_usd",
        "review_rating"
    ]

    missing_columns = [
        col for col in required_columns if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Data quality checks
    assert df["customer_id"].notna().all(), \
        "Customer IDs contain missing values"

    assert df["customer_id"].is_unique, \
        "Customer IDs are not unique"

    assert df["age"].between(0, 120).all(), \
        "Invalid age values found"

    assert df["purchase_amount_usd"].ge(0).all(), \
        "Negative purchase amounts found"

    assert df["review_rating"].dropna().between(1, 5).all(), \
        "Invalid review ratings found"

    # Save cleaned dataset
    output = PROCESSED_DIR / "customer_shopping_clean.csv"

    df.to_csv(output, index=False)

    # Cleaning report
    print("\nCleaning completed successfully!")
    print("Final shape:", df.shape)
    print("Removed duplicates:", removed_duplicates)
    print("Missing values:", df.isna().sum().sum())
    print("Remaining duplicates:", df.duplicated().sum())
    print("Saved file:", output)


# ==================================================
# 4. CLEAN ONLINE RETAIL DATA
# ==================================================

def clean_retail_data():

    print("\n" + "=" * 50)
    print("ONLINE RETAIL DATA CLEANING")
    print("=" * 50)

    path = RAW_DIR / "online_retail.csv"

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)

    print("Original shape:", df.shape)

    # Standardize column names
    df = standardize_columns(df)

    print("\nStandardized columns:")
    print(df.columns.tolist())

    # Validate required columns
    required_columns = [
        "invoice_no",
        "stock_code",
        "description",
        "quantity",
        "invoice_date",
        "unit_price",
        "customer_id",
        "country"
    ]

    missing_columns = [
        col for col in required_columns if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Remove exact duplicates
    initial_rows = len(df)
    df = df.drop_duplicates()
    removed_duplicates = initial_rows - len(df)

    # Clean descriptions
    df["description"] = (
        df["description"]
        .fillna("Unknown Product")
        .astype(str)
        .str.strip()
    )

    # Clean identifiers
    df["invoice_no"] = (
        df["invoice_no"].astype(str).str.strip()
    )

    df["stock_code"] = (
        df["stock_code"].astype(str).str.strip()
    )

    # Convert invoice date
    df["invoice_date"] = pd.to_datetime(
        df["invoice_date"],
        errors="coerce"
    )

    # Convert numeric columns
    df["quantity"] = pd.to_numeric(
        df["quantity"],
        errors="coerce"
    )

    df["unit_price"] = pd.to_numeric(
        df["unit_price"],
        errors="coerce"
    )

    df["customer_id"] = pd.to_numeric(
        df["customer_id"],
        errors="coerce"
    ).astype("Int64")

    # Remove records with invalid essential transaction fields.
    # Missing customer IDs are intentionally preserved.
    df = df.dropna(
        subset=[
            "invoice_no",
            "stock_code",
            "invoice_date",
            "quantity",
            "unit_price"
        ]
    )

    # Create business features
    df["total_amount"] = (
        df["quantity"] * df["unit_price"]
    )

    df["invoice_year"] = df["invoice_date"].dt.year

    df["invoice_month"] = df["invoice_date"].dt.month

    df["invoice_hour"] = df["invoice_date"].dt.hour

    # Identify cancelled invoices
    df["is_cancelled"] = (
        df["invoice_no"]
        .str.upper()
        .str.startswith("C")
    )

    # Identify returns / negative quantities
    df["is_return"] = df["quantity"] < 0

    # Flag zero or negative prices
    df["is_zero_or_negative_price"] = (
        df["unit_price"] <= 0
    )

    # Save cleaned dataset
    output = PROCESSED_DIR / "online_retail_clean.csv"

    df.to_csv(output, index=False)

    # Cleaning report
    print("\nCleaning completed successfully!")
    print("Final shape:", df.shape)
    print("Removed duplicates:", removed_duplicates)

    print(
        "Missing customer IDs:",
        df["customer_id"].isna().sum()
    )

    print(
        "Cancelled invoices:",
        df["is_cancelled"].sum()
    )

    print(
        "Return records:",
        df["is_return"].sum()
    )

    print(
        "Zero/negative price records:",
        df["is_zero_or_negative_price"].sum()
    )

    print("Remaining duplicates:", df.duplicated().sum())
    print("Saved file:", output)


# ==================================================
# 5. MAIN EXECUTION
# ==================================================

def main():

    print("\n")
    print("#" * 50)
    print("       BENCHMARKLAB AI - DATA PIPELINE")
    print("#" * 50)

    clean_shopping_data()

    clean_retail_data()

    print("\n" + "#" * 50)
    print("ALL DATA CLEANING TASKS COMPLETED")
    print("#" * 50)


if __name__ == "__main__":
    main()
