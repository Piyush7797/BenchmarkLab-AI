
from ucimlrepo import fetch_ucirepo
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "raw"

DATA_DIR.mkdir(parents=True, exist_ok=True)

print("Fetching Online Retail dataset...")

dataset = fetch_ucirepo(id=352)

# Extract both dataframes
features = dataset.data.features.copy()
identifiers = dataset.data.ids.copy()

# Validate row alignment
if len(features) != len(identifiers):
    raise ValueError("Feature and identifier row counts differ!")

if not features.index.equals(identifiers.index):
    raise ValueError("Feature and identifier indexes do not match!")

# Reconstruct complete dataset
df = pd.concat(
    [identifiers, features],
    axis=1
)

# Validate schema
expected_columns = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country"
]

if df.columns.tolist() != expected_columns:
    raise ValueError("Unexpected dataset schema!")

# Save complete raw dataset
output_path = DATA_DIR / "online_retail.csv"

df.to_csv(output_path, index=False)

print("\nDataset reconstructed successfully!")
print("Shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate records:", df.duplicated().sum())
print("\nSample records:")
print(df.head())

print("\nSaved:", output_path)
