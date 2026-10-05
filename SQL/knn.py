# %%
# Importing necessary libraries
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.datasets import load_iris
import matplotlib.pyplot as plt
import seaborn as sns
# %%
# Load the cancer dataset
df = pd.read_csv("Cancer_Prediction.csv")
df.head()
# %%
# X and Y

X = df.drop(columns=['diagnosis', 'id', 'Unnamed: 32'])
y = df['diagnosis']
# %%
# REMOVE MISSING VALUES

X = X.dropna()
y = y.loc[X.index]
# %%
# SPLIT THE DATASET

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)
# %%
from sklearn.preprocessing import StandardScaler
# %%
# FEATURE SCALING

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# %%
# KNN MODEL

knn = KNeighborsClassifier(n_neighbors=3)

knn.fit(X_train, y_train)

y_pred = knn.predict(X_test)
# %%
# KNN ACCURACY

accuracy = accuracy_score(y_test, y_pred)

print("KNN Accuracy:", accuracy)
print("KNN Accuracy:", accuracy * 100, "%")
# Fit the model on training data
knn.fit(X_train, y_train)


# %%
