# %%
# Import necessary libraries

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# %%
# Loading the dataset

df = pd.read_csv("Cancer_Prediction.csv")
df.head()

# %%
# SELECT FEATURES

diagnosis = df["diagnosis"]

X = df.drop(columns=["diagnosis", "id", "Unnamed: 32"])

# %%
# REMOVE MISSING VALUES

X = X.dropna()
diagnosis = diagnosis.loc[X.index]

# %%
# STANDARDIZE THE DATA

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# %%
# K-MEANS CLUSTERING

kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
kmeans.fit(X_scaled)

# %%
# %%
# ADD CLUSTER ASSIGNMENTS

df = df.loc[X.index].copy()

df["Cluster"] = kmeans.labels_

df.head()
# %%
# VISUALIZE THE CLUSTERS

plt.figure(figsize=(8, 6))

plt.scatter(
    X_scaled[:, 0],
    X_scaled[:, 1],
    c=kmeans.labels_,
    cmap="viridis",
    marker="o",
    edgecolor="k"
)

plt.title("K-Means Clustering - Cancer Dataset")
plt.xlabel(X.columns[0])
plt.ylabel(X.columns[1])

plt.show()

# %%
# PRINT CENTROIDS AND INERTIA

print("Centroids of clusters:")
print(kmeans.cluster_centers_)

print("\nInertia:", kmeans.inertia_)

# %%
# DATA WITH CLUSTER ASSIGNMENTS

print(df.head())

# %%
