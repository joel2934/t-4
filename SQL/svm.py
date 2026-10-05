# %%
# IMPORTING NECESSARY LIBRARIES

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns


# %%
# LOAD THE CANCER DATASET

df = pd.read_csv("Cancer_Prediction.csv")
df.head()


# %%
# X AND Y

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
# FEATURE SCALING

from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


# %%
# SVM MODEL

svm = SVC()

svm.fit(X_train, y_train)

y_pred = svm.predict(X_test)


# %%
# SVM ACCURACY

accuracy = accuracy_score(y_test, y_pred)

print("SVM Accuracy:", accuracy)
print("SVM Accuracy:", accuracy * 100, "%")