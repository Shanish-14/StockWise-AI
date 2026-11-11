
import pandas as pd

# Load the original dataset
file_path = "data/raw/demand/train.parquet"

df = pd.read_parquet(file_path)

# Display basic information
print("DATASET LOADED SUCCESSFULLY!")

print("\nDataset shape:")
print(df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nDataset information:")
df.info()

print("\nMissing values:")
print(df.isnull().sum())

