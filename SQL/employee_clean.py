# %%
# IMPORT LIBRARIES

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (
    LabelEncoder,
    OneHotEncoder,
    StandardScaler,
    MinMaxScaler
)
from sklearn.impute import SimpleImputer
# %%
# READ DATASET

df = pd.read_csv("employee_data.csv")

df.head()
# %%
# BASIC INFORMATION

print("Shape:", df.shape)

df.info()
# %%
# COLUMN NAMES
print("Column:" ,df.columns)

# %%
# VIEW DATA
print(df.head(10))

# %%
# STATISTICAL SUMMARY
print(df.describe())

# %%
# FIND MISSING VALUES

print(df.isnull().sum())
# %%
# COLUMNS WITH MISSING VALUES

print(df.isnull().sum()[df.isnull().sum() > 0])

# %%
# FILL AGE MISSING VALUES WITH MEAN

df["Age"] = df["Age"].fillna(
    df["Age"].mean()
)
# %%
# FILL SALARY MISSING VALUES WITH MEDIAN
df["Salary"] = df["Salary"].fillna(
    df["Salary"].median()
)
# %%
# FILL DEPARTMENT MISSING VALUES WITH MODE
df["Department"] = df["Department"].fillna(
    df["Department"].mode()[0]
)
# %%
# FILL PERFORMANCE SCORE MISSING VALUES WITH MEDIAN
df["PerformanceScore"] = df["PerformanceScore"].fillna(
    df["PerformanceScore"].median()
)
# %%
# VERIFY MISSING VALUES

print(df.isnull().sum())

# %%
# CHECK TOTAL MISSING VALUES

print("Total missing values:", df.isnull().sum().sum())
# %%
# FILL MISSING JOINING DATE

df["JoiningDate"] = df["JoiningDate"].fillna(
    df["JoiningDate"].mode()[0]
)

# %%
# VERIFY

print(df["JoiningDate"].isnull().sum())

# %%
# VERIFY MISSING VALUES

print(df.isnull().sum())

# %%
# VIEW DATA
print(df.head(50))

# %%
# CONVERT JOINING DATE TO DATETIME

df["JoiningDate"] = pd.to_datetime(
    df["JoiningDate"],
    errors="coerce"
)

df["JoiningDate"].head()

# %%
# EXTRACT JOINING YEAR

df["joining_year"] = df["JoiningDate"].dt.year

# %%
# EXTRACT JOINING MONTH

df["joining_month"] = df["JoiningDate"].dt.month

# %%
# EXTRACT JOINING DAY

df["joining_day"] = df["JoiningDate"].dt.day

# %%
# EMPLOYEES JOINED AFTER 2010

count = (df["joining_year"] > 2010).sum()

print("Employees joined after 2010:", count)

# %%
# SPLIT CONTACT COLUMN

df[["Email", "Phone"]] = df["Contact"].str.split(
    "|",
    expand=True
)

# %%
# REMOVE SPACES

df["Email"] = df["Email"].str.strip()
df["Phone"] = df["Phone"].str.strip()

# %%
# DROP CONTACT COLUMN

df = df.drop(
    columns=["Contact"]
)

# %%
# CREATE BONUS COLUMN

df["Bonus"] = df["Salary"] * 0.10

# %%
# CREATE TOTAL SALARY

df["TotalSalary"] = df["Salary"] + df["Bonus"]

# %%
# CREATE ANNUAL SALARY

df["AnnualSalary"] = df["Salary"] * 12

# %%
# EXPERIENCE AFTER 5 YEARS

df["ExperienceAfter5Years"] = df["Experience"] + 5

# %%
# VIEW NEW COLUMNS

df[
    [
        "Name",
        "Salary",
        "Email",
        "Phone",
        "Bonus",
        "TotalSalary",
        "AnnualSalary",
        "ExperienceAfter5Years"
    ]
].head()
# %%
