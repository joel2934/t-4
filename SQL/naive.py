# %%
# IMPORT LIBRARIES

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report

# %%
# LOAD DATASET

df = pd.read_csv("spam_ham_dataset.csv")
df.head()
# %%
# DATA INFORMATION

print(df.shape)
print(df.columns)
df.isnull().sum()

# %%
# SELECT REQUIRED COLUMNS

df = df[["label", "message"]]

# %%
# REMOVE MISSING VALUES

df.dropna(inplace=True)
# %%
# SEPARATE FEATURES AND TARGET

X = df["message"]
y = df["label"]
# %%
# ENCODE TARGET

y = y.map({"ham": 0, "spam": 1})

# %%
# SPLIT DATASET

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)
# %%
# CONVERT TEXT TO NUMBERS

vectorizer = CountVectorizer()

X_train = vectorizer.fit_transform(X_train)
X_test = vectorizer.transform(X_test)

# %%
# CREATE NAIVE BAYES MODEL

nb_classifier = MultinomialNB()

nb_classifier.fit(X_train, y_train)
# %%
# MAKE PREDICTIONS

y_pred = nb_classifier.predict(X_test)
# %%
# CALCULATE ACCURACY

accuracy = accuracy_score(y_test, y_pred)

print("Accuracy:", accuracy)
print("Accuracy:", accuracy * 100, "%")
# %%
