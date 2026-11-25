
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")

def inspect_dataset(file_path):

    print("\n" + "=" * 55)
    print(f"DATASET: {file_path.name}")
    print("=" * 55)

    df = pd.read_csv(file_path)

    print("\n1. Dataset Shape")
    print(df.shape)

    print("\n2. Column Names")
    print(df.columns.tolist())

    print("\n3. Data Types")
    print(df.dtypes)

    print("\n4. Missing Values")
    print(df.isnull().sum())

    print("\n5. Duplicate Records")
    print(df.duplicated().sum())

    print("\n6. Statistical Summary")
    print(df.describe(include="all").T)

    print("\n7. Sample Records")
    print(df.head())


if __name__ == "__main__":

    files = list(DATA_DIR.glob("*.csv"))

    if not files:
        print("No CSV files found in data/raw/")
    else:
        for file in files:
            inspect_dataset(file)
