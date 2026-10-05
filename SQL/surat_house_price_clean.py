# %%
# IMPORT LIBRARIES

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler, MinMaxScaler
from sklearn.impute import SimpleImputer

# %%
# LOAD DATASET

df = pd.read_csv("surat_house_price.csv")

df.head()
# %%
# CHECK SHAPE

print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

# %%
# COLUMN NAMES

print(df.columns)

# %%
# DATA INFORMATION

df.info()

# %%
# STATISTICAL SUMMARY

df.describe(include="all")

# %%
# MISSING VALUES

print(df.isnull().sum())

# %%
# COLUMNS WITH MISSING VALUES

missing = df.isnull().sum()

print(missing[missing > 0])
# %%
# CHECK DUPLICATES

print("Duplicate rows:", df.duplicated().sum())
# %%
# REMOVE DUPLICATES

df = df.drop_duplicates()

print("Rows after removing duplicates:", len(df))
# %%
# STANDARDISE COLUMN NAMES

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# %%
# REMOVE UNWANTED SPACES

for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].str.strip()

# %%
# FILL TRANSACTION

df["transaction"] = df["transaction"].fillna(
    df["transaction"].mode()[0]
)

# %%
# FILL STATUS

df["status"] = df["status"].fillna(
    df["status"].mode()[0]
)

# %%
# FILL FURNISHING

df["furnishing"] = df["furnishing"].fillna(
    df["furnishing"].mode()[0]
)
# %%
# FILL FACING

df["facing"] = df["facing"].fillna(
    df["facing"].mode()[0]
)
# %%
# %%
# FILL DESCRIPTION

df["description"] = df["description"].fillna("")

# %%
# VERIFY MISSING VALUES

print(df.isnull().sum())

# %%
# CLEAN AND STANDARDISE SQUARE FEET

df["square_feet"] = df["square_feet"].str.strip().str.lower()

df["square_feet"] = np.where(
    df["square_feet"].str.contains("sqm", na=False),
    pd.to_numeric(
        df["square_feet"].str.replace("sqm", "", regex=False).str.strip(),
        errors="coerce"
    ) * 10.7639,
    pd.to_numeric(
        df["square_feet"].str.replace("sqft", "", regex=False).str.strip(),
        errors="coerce"
    )
)

# %%
# CLEAN PRICE PER SQFT

df["price_per_sqft"] = (
    df["price_per_sqft"]
    .str.replace("₹", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.replace("per sqft", "", regex=False)
    .str.strip()
)

df["price_per_sqft"] = pd.to_numeric(
    df["price_per_sqft"],
    errors="coerce"
)
# %%
# CLEAN PRICE

df["price"] = (
    df["price"]
    .str.replace("₹", "", regex=False)
    .str.strip()
)

df["price"] = df["price"].str.replace(
    "Lac",
    "",
    regex=False
).str.strip()

df["price"] = pd.to_numeric(
    df["price"],
    errors="coerce"
) * 100000


# %%
# FILL PRICE PER SQFT

df["price_per_sqft"] = df["price_per_sqft"].fillna(
    df["price_per_sqft"].median()
)
# %%
# FILL SQUARE FEET

df["square_feet"] = df["square_feet"].fillna(
    df["square_feet"].median()
)

# %%
# FINAL MISSING VALUE CHECK

print(df.isnull().sum())
# %%
# TOTAL MISSING VALUES

print(
    "Total missing values:",
    df.isnull().sum().sum()
)
# %%
