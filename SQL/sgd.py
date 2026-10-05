# %%
# Importing necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import SGDRegressor

from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
# %%
# Load the dataset
df = pd.read_csv("kc_house_data.csv")
df.head(5)

# %%
# Summary of the dataset
df.info()
df.isnull().sum()

# %%
# Features and Target Variable
X = df[[
    'sqft_living',
    'bedrooms',
    'bathrooms',
    'floors',
    'condition'
]]

y = df['price']

# %%
#TRAINING
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)
# %%
#fit trans
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
batch_model = LinearRegression()
batch_model.fit(X_train, y_train)
batch_predictions = batch_model.predict(X_test)

# %%
batch_mse = mean_squared_error(y_test, batch_predictions)

batch_r2 = r2_score(y_test, batch_predictions)

print("Batch Learning MSE:", batch_mse)
print("Batch Learning R2 Score:", batch_r2)
# %%
#coef
print(batch_model.coef_)
#intercept
print(batch_model.intercept_)

# %%
X_initial = X_train_scaled[:5000]
y_initial = y_train.iloc[:5000]

X_stream = X_train_scaled[5000:]
y_stream = y_train.iloc[5000:]
incremental_model = SGDRegressor(
    learning_rate='constant',
    eta0=0.000001,
    max_iter=1,
    tol=None,
    random_state=42
)
#initial training
incremental_model.partial_fit(X_initial, y_initial)

# %%
#now lets stream new data
batch_size = 500

for i in range(0, len(X_stream), batch_size):

    X_batch = X_stream[i:i+batch_size]
    y_batch = y_stream.iloc[i:i+batch_size]

    incremental_model.partial_fit(X_batch, y_batch)

    print(f"Updated using rows {i} to {i+batch_size}")

# %%
