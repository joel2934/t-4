# %%
# IMPORT NECESSARY LIBRARIES

import numpy as np
import pandas as pd

from sklearn.model_selection import (
    train_test_split,
    KFold,
    StratifiedKFold,
    LeaveOneOut,
    cross_val_score
)

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score
)

from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.utils import resample
# %%
# LOAD CANCER DATASET

df = pd.read_csv("Cancer_Prediction.csv")

df.head()

# %%
# DATASET INFORMATION

print("Shape:", df.shape)
print("Columns:", df.columns)
print("\nMissing Values:")
print(df.isnull().sum())

# %%
# SEPARATE FEATURES AND TARGET

X = df.drop(columns=["diagnosis", "id", "Unnamed: 32"])
y = df["diagnosis"]

# %%
# REMOVE MISSING VALUES

X = X.dropna()
y = y.loc[X.index]

# %%
# ENCODE TARGET

y = y.map({
    "B": 0,
    "M": 1
})

# %%
# CREATE LOGISTIC REGRESSION PIPELINE

model = Pipeline([
    ("scaler", StandardScaler()),
    ("logistic", LogisticRegression(max_iter=5000))
])

# %%
# TRAIN-TEST SPLIT

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

tt_accuracy = accuracy_score(y_test, y_pred)

print("Train-Test Accuracy:", round(tt_accuracy, 4))

# %%
# INSTABILITY OF TRAIN-TEST SPLIT

for i in range(5):

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2
    )

    model.fit(X_train, y_train)

    acc = model.score(X_test, y_test)

    print(f"Run {i+1}: Accuracy = {round(acc, 4)}")



# %%
# K-FOLD CROSS VALIDATION

kf = KFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

kf_scores = cross_val_score(
    model,
    X,
    y,
    cv=kf
)

print("K-Fold Scores:", np.round(kf_scores, 4))
print("Mean Accuracy:", round(kf_scores.mean(), 4))

# %%
# STRATIFIED K-FOLD CROSS VALIDATION

skf = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

skf_scores = cross_val_score(
    model,
    X,
    y,
    cv=skf
)

print("Stratified K-Fold Scores:", np.round(skf_scores, 4))
print("Mean Accuracy:", round(skf_scores.mean(), 4))

# %%
# LEAVE-ONE-OUT CROSS VALIDATION

loo = LeaveOneOut()

loo_scores = cross_val_score(
    model,
    X,
    y,
    cv=loo
)

print("LOOCV Mean Accuracy:", round(loo_scores.mean(), 4))

# %%
# BOOTSTRAP EVALUATION

accuracies = []

for i in range(10):

    X_sample, y_sample = resample(
        X,
        y,
        replace=True,
        n_samples=len(X),
        random_state=i
    )

    model.fit(X_sample, y_sample)

    y_pred = model.predict(X)

    acc = accuracy_score(y, y_pred)

    accuracies.append(acc)

print("Bootstrap Accuracies:", accuracies)
print("Mean Accuracy:", np.mean(accuracies))

# %%
# CONFUSION MATRIX

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
# %%
# CLASSIFICATION REPORT

print(
    classification_report(
        y_test,
        y_pred,
        target_names=["Benign", "Malignant"]
    )
)

# %%
# SINGLE MODEL EVALUATION

scores = cross_val_score(
    model,
    X,
    y,
    cv=5
)

print("Scores:", np.round(scores, 4))
print("Mean:", round(scores.mean(), 4))
print("Std Dev:", round(scores.std(), 4))

# %%
# MODEL COMPARISON

model1 = Pipeline([
    ("scaler", StandardScaler()),
    ("logistic", LogisticRegression(max_iter=5000))
])

model2 = DecisionTreeClassifier(random_state=42)

scores1 = cross_val_score(
    model1,
    X,
    y,
    cv=5
)

scores2 = cross_val_score(
    model2,
    X,
    y,
    cv=5
)

print("Model Comparison")

print(
    "Logistic Regression:",
    round(scores1.mean(), 4)
)

print(
    "Decision Tree:",
    round(scores2.mean(), 4)
)

# %%
# PAIRED MODEL COMPARISON

kf = KFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

scores1 = []
scores2 = []

for train_idx, test_idx in kf.split(X):

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]

    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    model1.fit(X_train, y_train)
    model2.fit(X_train, y_train)

    scores1.append(
        model1.score(X_test, y_test)
    )

    scores2.append(
        model2.score(X_test, y_test)
    )

print("Model 1 Scores:", scores1)
print("Model 2 Scores:", scores2)

diff = np.array(scores1) - np.array(scores2)

print("Difference:", diff)

# %%
# FINAL COMPARISON

results = {
    "Train-Test Split": tt_accuracy,
    "K-Fold (5)": kf_scores.mean(),
    "Stratified K-Fold (5)": skf_scores.mean(),
    "LOOCV": loo_scores.mean()
}

for method, score in results.items():
    print(
        f"{method:<25} : {round(score, 4)}"
    )

# %%
