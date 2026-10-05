# %%
# IMPORT LIBRARIES

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
# %%
# LOAD DATASET

df = pd.read_csv("ecommerce_dataset.csv")

df.head()
# %%
# DATA INFORMATION

df.info()

# %%
# DATASET SHAPE

print("Rows:", df.shape[0])
print("Columns:", df.shape[1])
# %%
# CHECK MISSING VALUES

print(df.isnull().sum())


# %%
# CHECK DUPLICATES

print("Duplicate rows:", df.duplicated().sum())
# %%
# CONVERT ORDER DATE

df["Order_Date"] = pd.to_datetime(
    df["Order_Date"],
    errors="coerce"
)

df.head()
# %%
# CHECK DATA TYPES

print(df.dtypes)

# %%
# SET PLOT STYLE

sns.set_theme(style="whitegrid")


# %%
# TOTAL SALES BY DATE

daily_sales = df.groupby(
    "Order_Date"
)["Sales"].sum()

plt.figure(figsize=(12, 5))

plt.plot(
    daily_sales.index,
    daily_sales.values
)

plt.xlabel("Date")
plt.ylabel("Total Sales")
plt.title("Total Sales by Date")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
# %%
# TOTAL PROFIT BY DATE

daily_profit = df.groupby(
    "Order_Date"
)["Profit"].sum()

plt.figure(figsize=(12, 5))

plt.plot(
    daily_profit.index,
    daily_profit.values
)

plt.xlabel("Date")
plt.ylabel("Total Profit")
plt.title("Total Profit by Date")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
# %%
# CREATE MONTH COLUMN

df["Month"] = df["Order_Date"].dt.to_period("M")

# %%
# MONTHLY SALES

monthly_sales = df.groupby(
    "Month"
)["Sales"].sum()

print(monthly_sales)

# %%
# MONTHLY SALES PLOT

plt.figure(figsize=(10, 5))

plt.plot(
    monthly_sales.index.astype(str),
    monthly_sales.values,
    marker="o"
)

plt.xlabel("Month")
plt.ylabel("Total Sales")
plt.title("Monthly Sales")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %%
# HIGHEST SALES MONTH

highest_month = monthly_sales.idxmax()
highest_sales = monthly_sales.max()

print("Highest Sales Month:", highest_month)
print("Sales:", highest_sales)

# %%
# SALES BY CATEGORY

category_sales = df.groupby(
    "Category"
)["Sales"].sum()

plt.figure(figsize=(8, 5))

sns.barplot(
    x=category_sales.index,
    y=category_sales.values
)

plt.xlabel("Category")
plt.ylabel("Total Sales")
plt.title("Sales by Product Category")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %%
# PROFIT BY CITY

city_profit = df.groupby(
    "City"
)["Profit"].sum().sort_values(ascending=False)

plt.figure(figsize=(10, 5))

sns.barplot(
    x=city_profit.index,
    y=city_profit.values
)

plt.xlabel("City")
plt.ylabel("Total Profit")
plt.title("Profit Across Cities")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %%
# TOP 5 PRODUCTS BY SALES

product_sales = (
    df.groupby("Product")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)

print(product_sales)

# %%
# ORDERS BY PAYMENT MODE

payment_orders = df["Payment_Mode"].value_counts()

plt.figure(figsize=(8, 5))

sns.barplot(
    x=payment_orders.index,
    y=payment_orders.values
)

plt.xlabel("Payment Mode")
plt.ylabel("Number of Orders")
plt.title("Orders by Payment Mode")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %%
# SALES DISTRIBUTION

plt.figure(figsize=(8, 5))

sns.histplot(
    df["Sales"],
    bins=20
)

plt.xlabel("Sales")
plt.ylabel("Frequency")
plt.title("Distribution of Sales")

plt.tight_layout()
plt.show()

# %%
# PROFIT DISTRIBUTION

plt.figure(figsize=(8, 5))

sns.histplot(
    df["Profit"],
    bins=20
)

plt.xlabel("Profit")
plt.ylabel("Frequency")
plt.title("Distribution of Profit")

plt.tight_layout()
plt.show()

# %%
# QUANTITY DISTRIBUTION

plt.figure(figsize=(8, 5))

sns.histplot(
    df["Quantity"],
    bins=10
)

plt.xlabel("Quantity")
plt.ylabel("Frequency")
plt.title("Distribution of Quantity")

plt.tight_layout()
plt.show()

# %%
# QUANTITY WITH DIFFERENT BINS

plt.figure(figsize=(8, 5))

sns.histplot(
    df["Quantity"],
    bins=5
)

plt.title("Quantity Distribution - 5 Bins")
plt.xlabel("Quantity")
plt.ylabel("Frequency")

plt.show()

# %%
# QUANTITY WITH MORE BINS

plt.figure(figsize=(8, 5))

sns.histplot(
    df["Quantity"],
    bins=20
)

plt.title("Quantity Distribution - 20 Bins")
plt.xlabel("Quantity")
plt.ylabel("Frequency")

plt.show()

# %%
# BOX PLOT - SALES

plt.figure(figsize=(8, 5))

sns.boxplot(
    y=df["Sales"]
)

plt.title("Box Plot of Sales")
plt.ylabel("Sales")

plt.show()

# %%
# BOX PLOT - PROFIT

plt.figure(figsize=(8, 5))

sns.boxplot(
    y=df["Profit"]
)

plt.title("Box Plot of Profit")
plt.ylabel("Profit")

plt.show()

# %%
# SALES BY CATEGORY - BOX PLOT

plt.figure(figsize=(10, 6))

sns.boxplot(
    x="Category",
    y="Sales",
    data=df
)

plt.xlabel("Category")
plt.ylabel("Sales")
plt.title("Sales Distribution by Category")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %%
# ORDERS BY CATEGORY

category_orders = df["Category"].value_counts()

plt.figure(figsize=(7, 7))

plt.pie(
    category_orders.values,
    labels=category_orders.index,
    autopct="%1.1f%%"
)

plt.title("Percentage of Orders by Category")

plt.show()

# %%
# ORDERS BY PAYMENT MODE

payment_orders = df["Payment_Mode"].value_counts()

plt.figure(figsize=(7, 7))

plt.pie(
    payment_orders.values,
    labels=payment_orders.index,
    autopct="%1.1f%%"
)

plt.title("Percentage of Orders by Payment Mode")

plt.show()

# %%
# ORDERS BY CITY

city_orders = df["City"].value_counts()

plt.figure(figsize=(8, 8))

plt.pie(
    city_orders.values,
    labels=city_orders.index,
    autopct="%1.1f%%"
)

plt.title("Percentage of Orders by City")

plt.show()

# %%
