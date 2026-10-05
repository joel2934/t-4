# %%
# IMPORTS

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W

# %%
# SPARK SESSION

spark = SparkSession.builder \
    .appName("CSV Analysis") \
    .master("local[*]") \
    .getOrCreate()

# %%
# LOAD CSV

df = spark.read.csv(
    "dataset.csv",
    header=True,
    inferSchema=True
)
# %%
# SHOW DATA

df.show()
# %%
df.printSchema()

# %%
import re
new_column_names = []
for c in df.columns:
    new_name = c.strip()
    new_name = re.sub(r'[\s-]+', '_', new_name)
    new_name = re.sub(r'[^a-zA-Z0-9_]', '', new_name)
    new_name = re.sub(r'_+', '_', new_name)
    new_name = new_name.lower()
    new_column_names.append(new_name)

# %%
# OLD AND NEW COLUMN NAMES

column_mapping = list(zip(df.columns, new_column_names))

for old, new in column_mapping:
    print(old, "->", new)

# %%
# CHECK CHANGED COLUMN NAMES

for old, new in column_mapping:
    if old != new:
        print(f"Changed: {old} -> {new}")

# %%
# RENAME COLUMNS

df = df.toDF(*new_column_names)

df.show()
# %%
# %%
import re
new_column_names = []
for c in df.columns:
    new_name = c.strip()
    new_name = re.sub(r'[\s-]+', '_', new_name)
    new_name = re.sub(r'[^a-zA-Z0-9_]', '', new_name)
    new_name = re.sub(r'_+', '_', new_name)
    new_name = new_name.lower()
    new_column_names.append(new_name)

# %%
# OLD AND NEW COLUMN NAMES

column_mapping = list(zip(df.columns, new_column_names))

for old, new in column_mapping:
    print(old, "->", new)

# %%
# CHECK CHANGED COLUMN NAMES

for old, new in column_mapping:
    if old != new:
        print(f"Changed: {old} -> {new}")

# %%
# RENAME COLUMNS

df = df.toDF(*new_column_names)
df.show()

# %%
df.dtypes

# %%
# STANDARDISE IS_ACTIVE

df = df.withColumn(
    "is_active",
    F.when(
        F.upper(F.trim(F.col("is_active"))).isin("Y", "YES", "1", "TRUE", "ACTIVE"),
        "YES"
    )
    .when(
        F.upper(F.trim(F.col("is_active"))).isin("N", "NO", "0", "FALSE", "INACTIVE"),
        "NO"
    )
    .otherwise(None)
)

df.show(truncate=False)

# %%
# STANDARDISE SEX

df = df.withColumn(
    "sex",
    F.when(
        F.upper(F.trim(F.col("sex"))).isin("F", "FEMALE"),
        "F"
    )
    .when(
        F.upper(F.trim(F.col("sex"))).isin("M", "MALE"),
        "M"
    )
    .otherwise(None)
)

df.show(truncate=False)
# %%
# CHECK STANDARDISED VALUES

df.select("is_active", "sex").show(truncate=False)

# %%
# STANDARDISE AMOUNT

df = df.withColumn(
    "amount",
    F.trim(F.col("amount"))
)

df = df.withColumn(
    "amount",
    F.when(
        F.col("amount").isin("-", "NA", "N/A", "NULL", "NONE", ""),
        None
    )
    .otherwise(F.col("amount"))
)

df = df.withColumn(
    "amount",
    F.regexp_replace(F.col("amount"), " ", "")
)

df = df.withColumn(
    "amount",
    F.when(
        F.col("amount").contains(","),
        F.regexp_replace(
            F.regexp_replace(F.col("amount"), r"\.", ""),
            ",",
            "."
        )
    )
    .otherwise(
        F.regexp_replace(F.col("amount"), ",", "")
    )
)

df = df.withColumn(
    "amount",
    F.col("amount").cast("double").cast("int")
)

df = df.withColumn(
    "amount",
    F.abs(F.col("amount"))
)

df.show(truncate=False)
df.printSchema()
# %%
# STANDARDISE ORDER_DATE

df = df.withColumn(
    "order_date",
    F.trim(F.col("order_date"))
)

df = df.withColumn(
    "order_date",
    F.to_timestamp(
        F.col("order_date"),
        "M/d/yyyy H:mm"
    )
)

df = df.withColumn(
    "order_date",
    F.date_format(
        F.col("order_date"),
        "yyyy-MM-dd HH:mm"
    )
)
# %%
# STANDARDISE UPDATED_AT

df = df.withColumn(
    "updated_at",
    F.trim(F.col("updated_at"))
)

df = df.withColumn(
    "updated_at",
    F.to_timestamp(
        F.col("updated_at"),
        "M/d/yyyy H:mm"
    )
)

df = df.withColumn(
    "updated_at",
    F.date_format(
        F.col("updated_at"),
        "yyyy-MM-dd HH:mm"
    )
)

df.show(truncate=False)
df.printSchema()
# %%
# CREATE TEMP TABLE

df.createOrReplaceTempView("clean_data_temp")

# %%
# REMOVE DUPLICATES

df = spark.sql("""
    SELECT DISTINCT *
    FROM clean_data_temp
""")

df.show(truncate=False)
# %%
df = spark.sql("""
    SELECT *
    FROM clean_data_temp
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY id
        ORDER BY updated_at DESC
    ) = 1
""")

df.show(truncate=False)

# %%
# REMOVE DUPLICATES BASED ON ID

df.createOrReplaceTempView("clean_data_temp")

df = spark.sql("""
    SELECT *
    FROM (
        SELECT *,
               ROW_NUMBER() OVER (
                   PARTITION BY id
                   ORDER BY updated_at DESC
               ) AS rn
        FROM clean_data_temp
    ) t
    WHERE rn = 1
""").drop("rn")

df.show(df.count(), truncate=False)
# %%
print("Total rows:", df.count())
# %%
