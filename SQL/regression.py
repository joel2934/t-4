# %%
# Importing Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

# %%
# Load Dataset

df = pd.read_csv("kc_house_data.csv")
df.head()

# %%
# Data Information

df.info()
df.describe()
df.isnull().sum()

# %%
# Drop columns that are not needed for regression analysis
df.drop(columns=['id','date'], inplace=True)
# %%
# REMOVE MISSING VALUES

df.dropna(inplace=True)
# %%
# Checking for missing values after dropping rows with missing values
print(df.isnull().sum())
# %%
# SELECT IMPORTANT FEATURES

X = df[[
    "bedrooms",
    "bathrooms",
    "sqft_living",
    "floors",
    "grade",
    "sqft_above",
    "sqft_basement",
    "yr_built"
]]

y = df["price"]

# %%
# Checking for missing values in features
df.dropna(inplace=True)
missing = X.isnull().sum()
print(missing[missing > 0])
# %%
# Training and Testing Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# %%
# Model Training and Prediction
lr = LinearRegression()

lr.fit(X_train, y_train)

linear_pred = lr.predict(X_test)

# %%
# Values of Coefficients and Intercept
print("Linear Regression")

print("MAE :", mean_absolute_error(y_test, linear_pred))
print("MSE :", mean_squared_error(y_test, linear_pred))
print("RMSE:", np.sqrt(mean_squared_error(y_test, linear_pred)))
print("R2 Score:", r2_score(y_test, linear_pred))
# %%
# Polynomial Regression

poly_model = Pipeline([
    ("poly", PolynomialFeatures(degree=2)),
    ("linear", LinearRegression())
])

poly_model.fit(X_train, y_train)

poly_pred = poly_model.predict(X_test)

# %%
# Polynomial Regression Evaluation

print("Polynomial Regression")

print("MAE :", mean_absolute_error(y_test, poly_pred))
print("MSE :", mean_squared_error(y_test, poly_pred))
print("RMSE:", np.sqrt(mean_squared_error(y_test, poly_pred)))
print("R2 Score:", r2_score(y_test, poly_pred))

# %%
