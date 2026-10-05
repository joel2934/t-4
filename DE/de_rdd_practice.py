"""
Data Engineering / PySpark RDD Practice
Converted from the instructor's RDD.ipynb into one Python script.

Environment:
- Python 3.10
- PySpark 3.5.8
- Java 11
- Windows + VS Code
- Run from the project folder containing the input files.

Expected input files for all exercises:
    word_count_text.txt
    sales_data.csv
    nested_data.json

The instructor notebook also contains a Question 5 heading and several
RDD exercises. The stray `TRY` text has been removed because it is not
valid Python.
"""

# ============================================================
# 1. PYSPARK / WINDOWS CONFIGURATION
# ============================================================

import os
import sys
import re
import json
from pathlib import Path

# Use the Python interpreter of the currently active .venv.
# This avoids hard-coding the instructor's Anaconda path.
python_executable = sys.executable

os.environ["PYSPARK_PYTHON"] = python_executable
os.environ["PYSPARK_DRIVER_PYTHON"] = python_executable

# Windows/local-machine network configuration from the instructor setup.
os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--conf spark.driver.host=127.0.0.1 "
    "--conf spark.driver.bindAddress=127.0.0.1 "
    "--conf spark.python.worker.reuse=false "
    "--conf spark.network.timeout=600s "
    "--conf spark.executor.heartbeatInterval=60s "
    "pyspark-shell"
)

from pyspark.sql import SparkSession


# ============================================================
# 2. CREATE SPARK SESSION + SPARK CONTEXT
# ============================================================

spark = (
    SparkSession.builder
    .appName("DataEngineeringRDDPractice")
    .master("local[2]")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .config("spark.python.worker.reuse", "false")
    .config("spark.network.timeout", "600s")
    .getOrCreate()
)

sc = spark.sparkContext

print("=" * 60)
print("Spark started successfully")
print("Spark version:", spark.version)
print("Python:", python_executable)
print("=" * 60)

# ============================================================
# VIEW SALES DATA AS A TABLE
# ============================================================

sales_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv("sales_data.csv")
)

print("\n--- Sales Data Table ---")
sales_df.show(20, truncate=False)

print("\n--- Sales Data Schema ---")
sales_df.printSchema()


# ============================================================
# 3. BASIC RDD CREATION
# ============================================================

print("\n--- 3. Basic RDD Creation ---")

rdd = sc.parallelize([1, 2, 3, 4, 5])

print("RDD:", rdd.collect())


# ============================================================
# 4. BASIC RDD TRANSFORMATIONS - MAP
# ============================================================

print("\n--- 4. map() ---")

rdd = sc.parallelize([1, 2, 3, 4])

squared = rdd.map(lambda x: x * x)

print("Squared:", squared.collect())


# ============================================================
# 5. FILTER
# ============================================================

print("\n--- 5. filter() ---")

even = rdd.filter(lambda x: x % 2 == 0)

print("Even numbers:", even.collect())


# ============================================================
# 6. FLATMAP
# ============================================================

print("\n--- 6. flatMap() ---")

data = ["hello world", "spark is powerful"]

rdd = sc.parallelize(data)

words = rdd.flatMap(lambda x: x.split(" "))

print("Words:", words.collect())


# ============================================================
# 7. KEY-VALUE RDD
# ============================================================

print("\n--- 7. Key-Value RDD ---")

data = [
    ("a", 1),
    ("b", 2),
    ("a", 3),
    ("b", 4)
]

rdd = sc.parallelize(data)

print("Key-value RDD:", rdd.collect())


# ============================================================
# 8. reduceByKey()
# ============================================================

print("\n--- 8. reduceByKey() ---")

result = rdd.reduceByKey(lambda x, y: x + y)

print("reduceByKey:", result.collect())


# ============================================================
# 9. groupByKey()
# ============================================================

print("\n--- 9. groupByKey() ---")

result = rdd.groupByKey().mapValues(list)

print("groupByKey:", result.collect())


# ============================================================
# 10. RDD ACTIONS
# ============================================================

print("\n--- 10. RDD Actions ---")

rdd = sc.parallelize([10, 20, 30])

print("count():", rdd.count())
print("first():", rdd.first())
print("take(2):", rdd.take(2))
print("reduce():", rdd.reduce(lambda x, y: x + y))


# ============================================================
# 11. WORD COUNT + MOST REPEATED WORD
# ============================================================

print("\n--- 11. Word Count + Most Repeated Word ---")

word_file = Path("word_count_text.txt")

if word_file.exists():

    rdd = sc.textFile(str(word_file))

    # Split into words
    words = rdd.flatMap(lambda line: line.lower().split())

    # Remove punctuation
    words_clean = (
        words
        .map(lambda word: re.sub(r"[^a-z]", "", word))
        .filter(lambda word: word != "")
    )

    # Word Count
    word_count = (
        words_clean
        .map(lambda word: (word, 1))
        .reduceByKey(lambda a, b: a + b)
    )

    print("Word Count:")
    print(word_count.collect())

    # Most repeated word
    max_word = word_count.reduce(
        lambda a, b: a if a[1] > b[1] else b
    )

    print("Most repeated word:")
    print(max_word)

else:
    print("SKIPPED: word_count_text.txt not found.")


# ============================================================
# 12. EXTRA WORD QUESTIONS
# ============================================================

print("\n--- 12. Longest Word + Average Word Length ---")

if word_file.exists():

    # Reuse words_clean if the previous section ran.
    longest_word = words_clean.reduce(
        lambda a, b: a if len(a) > len(b) else b
    )

    print("Longest Word:", longest_word)
    print("Length:", len(longest_word))

    # Convert each word to (length, 1)
    length_rdd = words_clean.map(lambda w: (len(w), 1))

    # Sum lengths and counts
    total_length, total_words = length_rdd.reduce(
        lambda a, b: (
            a[0] + b[0],
            a[1] + b[1]
        )
    )

    average_length = total_length / total_words

    print("Average Word Length:", average_length)

else:
    print("SKIPPED: word_count_text.txt not found.")


# ============================================================
# 13. TOP 3 PRODUCTS BY TOTAL SALES
# ============================================================

print("\n--- 13. Top 3 Products by Total Sales ---")

sales_file = Path("sales_data.csv")

if sales_file.exists():

    rdd = sc.textFile(str(sales_file))

    # Remove header
    header = rdd.first()
    data = rdd.filter(lambda x: x != header)

    # Parse -> (product, amount)
    product_sales = (
        data
        .map(lambda x: x.split(","))
        .map(lambda x: (x[1], int(x[2])))
    )

    # Aggregate
    total_sales = product_sales.reduceByKey(
        lambda x, y: x + y
    )

    # Sort descending and take top 3
    top3 = (
        total_sales
        .sortBy(lambda x: x[1], ascending=False)
        .take(3)
    )

    print("Top 3 products:", top3)

else:
    print("SKIPPED: sales_data.csv not found.")


# ============================================================
# 14. SECOND HIGHEST SALE PER COUNTRY
# ============================================================

print("\n--- 14. Second Highest Sale Per Country ---")

if sales_file.exists():

    rdd = sc.textFile(str(sales_file))

    header = rdd.first()
    data = rdd.filter(lambda x: x != header)

    parsed = (
        data
        .map(lambda x: x.split(","))
        .map(lambda x: (x[0], int(x[2])))
    )

    # Group values by country
    grouped = parsed.groupByKey()

    # Find second highest
    second_highest = grouped.mapValues(
        lambda vals: (
            sorted(vals, reverse=True)[1]
            if len(list(vals)) > 1
            else None
        )
    )

    print("Second highest per country:")
    print(second_highest.collect())

else:
    print("SKIPPED: sales_data.csv not found.")


# ============================================================
# 15. REMOVE DUPLICATES WITHOUT distinct()
# ============================================================

print("\n--- 15. Remove Duplicates Without distinct() ---")

rdd = sc.parallelize([1, 2, 2, 3, 4, 4, 5])

unique = (
    rdd
    .map(lambda x: (x, 1))
    .reduceByKey(lambda x, y: x)
    .map(lambda x: x[0])
)

print("Unique values:", unique.collect())


# ============================================================
# 16. TOTAL SPENDING PER USER - JSON
# ============================================================

print("\n--- 16. Total Spending Per User ---")

json_file = Path("nested_data.json")

if json_file.exists():

    # The instructor's first version uses textFile + json.loads(line).
    # That only works when every line is a complete JSON object.
    #
    # The supplied notebook also contains a working wholeTextFiles
    # version, which is safer for a JSON array stored in one file.

    rdd = sc.wholeTextFiles(str(json_file))

    # Extract complete file content and parse the JSON.
    data = rdd.flatMap(lambda x: json.loads(x[1]))

    # Flatten:
    # user -> orders -> items
    user_spend = data.flatMap(
        lambda user: [
            (user["user"], item["price"])
            for order in user["orders"]
            for item in order["items"]
        ]
    )

    total = user_spend.reduceByKey(
        lambda x, y: x + y
    )

    print("Total spending per user:")
    print(total.collect())

else:
    print("SKIPPED: nested_data.json not found.")


# ============================================================
# 17. QUESTION 5: MOST SOLD PRODUCT (GLOBAL)
# ============================================================

print("\n--- 17. Question 5: Most Sold Product (Global) ---")

if sales_file.exists():

    rdd = sc.textFile(str(sales_file))

    header = rdd.first()
    data = rdd.filter(lambda x: x != header)

    product_count = (
        data
        .map(lambda x: x.split(",")[1])
        .map(lambda x: (x, 1))
        .reduceByKey(lambda x, y: x + y)
    )

    top_product = (
        product_count
        .sortBy(lambda x: x[1], ascending=False)
        .first()
    )

    print("Most sold product:", top_product)

else:
    print("SKIPPED: sales_data.csv not found.")


# ============================================================
# 18. JOIN TWO RDDs
# ============================================================

print("\n--- 18. Join Two RDDs ---")

users = sc.parallelize([
    ("u1", "Nishanth"),
    ("u2", "John")
])

transactions = sc.parallelize([
    ("u1", 100),
    ("u2", 200),
    ("u1", 50)
])

joined = users.join(transactions)

print("Joined RDD:")
print(joined.collect())


# ============================================================
# 19. DETECT DATA SKEW
# ============================================================

print("\n--- 19. Detect Data Skew ---")

if sales_file.exists():

    rdd = sc.textFile(str(sales_file))

    header = rdd.first()
    data = rdd.filter(lambda x: x != header)

    country_count = (
        data
        .map(lambda x: x.split(",")[0])
        .map(lambda x: (x, 1))
        .reduceByKey(lambda x, y: x + y)
    )

    # Example threshold from instructor notebook
    skewed = country_count.filter(
        lambda x: x[1] > 100
    )

    print("Country counts:")
    print(country_count.collect())

    print("Potentially skewed countries (>100):")
    print(skewed.collect())

else:
    print("SKIPPED: sales_data.csv not found.")


# ============================================================
# 20. SPARK SQL - BASIC OPERATIONS
# ============================================================

print("\n" + "=" * 60)
print("SPARK SQL - BASIC OPERATIONS")
print("=" * 60)


# ============================================================
# 20.1 LOAD EMPLOYEES CSV
# ============================================================

print("\n--- Loading Employees CSV ---")

employees_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv("employees_records.csv")
)


# ============================================================
# 20.2 VIEW EMPLOYEES TABLE
# ============================================================

print("\n--- Employees Table ---")

employees_df.show(20, truncate=False)


# ============================================================
# 20.3 VIEW SCHEMA
# ============================================================

print("\n--- Employees Schema ---")

employees_df.printSchema()


# ============================================================
# 20.4 CREATE SQL VIEW
# ============================================================

employees_df.createOrReplaceTempView("employees")


# ============================================================
# 20.5 SELECT ALL
# ============================================================

print("\n--- SELECT * ---")

spark.sql("""
    SELECT *
    FROM employees
""").show(20, truncate=False)


# ============================================================
# 20.6 SELECT SPECIFIC COLUMNS
# ============================================================

print("\n--- SELECT Specific Columns ---")

spark.sql("""
    SELECT name, salary
    FROM employees
""").show(20, truncate=False)


# ============================================================
# 20.7 GREATER THAN
# ============================================================

print("\n--- Salary > 7000 ---")

spark.sql("""
    SELECT *
    FROM employees
    WHERE salary > 7000
""").show(truncate=False)


# ============================================================
# 20.8 GREATER THAN OR EQUAL TO
# ============================================================

print("\n--- Salary >= 7000 ---")

spark.sql("""
    SELECT *
    FROM employees
    WHERE salary >= 7000
""").show(truncate=False)


# ============================================================
# 20.9 LESS THAN
# ============================================================

print("\n--- Salary < 7000 ---")

spark.sql("""
    SELECT *
    FROM employees
    WHERE salary < 7000
""").show(truncate=False)


# ============================================================
# 20.10 LESS THAN OR EQUAL TO
# ============================================================

print("\n--- Salary <= 7000 ---")

spark.sql("""
    SELECT *
    FROM employees
    WHERE salary <= 7000
""").show(truncate=False)


# ============================================================
# 20.11 EQUAL TO
# ============================================================

print("\n--- Salary = 7000 ---")

spark.sql("""
    SELECT *
    FROM employees
    WHERE salary = 7000
""").show(truncate=False)


# ============================================================
# 20.12 NOT EQUAL
# ============================================================

print("\n--- Salary != 7000 ---")

spark.sql("""
    SELECT *
    FROM employees
    WHERE salary != 7000
""").show(truncate=False)


# ============================================================
# 20.13 AND
# ============================================================

print("\n--- Salary > 7000 AND age > 30 ---")

spark.sql("""
    SELECT *
    FROM employees
    WHERE salary > 7000
      AND age > 30
""").show(truncate=False)


# ============================================================
# 20.14 OR
# ============================================================

print("\n--- Salary > 7000 OR age > 30 ---")

spark.sql("""
    SELECT *
    FROM employees
    WHERE salary > 7000
       OR age > 30
""").show(truncate=False)


# ============================================================
# 20.15 BETWEEN
# ============================================================

print("\n--- Salary BETWEEN 5000 AND 7000 ---")

spark.sql("""
    SELECT *
    FROM employees
    WHERE salary BETWEEN 5000 AND 7000
""").show(truncate=False)


# ============================================================
# 20.16 IN
# ============================================================

print("\n--- Department IN ---")

spark.sql("""
    SELECT *
    FROM employees
    WHERE department IN ('IT', 'HR')
""").show(truncate=False)


# ============================================================
# 20.17 NOT IN
# ============================================================

print("\n--- Department NOT IN ---")

spark.sql("""
    SELECT *
    FROM employees
    WHERE department NOT IN ('IT', 'HR')
""").show(truncate=False)


# ============================================================
# 20.18 LIKE
# ============================================================

print("\n--- Name LIKE ---")

spark.sql("""
    SELECT *
    FROM employees
    WHERE name LIKE 'A%'
""").show(truncate=False)


# ============================================================
# 20.19 COUNT EMPLOYEES
# ============================================================

print("\n--- Employee Count ---")

spark.sql("""
    SELECT COUNT(*) AS employee_count
    FROM employees
""").show()


# ============================================================
# 20.20 AVERAGE SALARY
# ============================================================

print("\n--- Average Salary ---")

spark.sql("""
    SELECT AVG(salary) AS average_salary
    FROM employees
""").show()


# ============================================================
# 20.21 MINIMUM SALARY
# ============================================================

print("\n--- Minimum Salary ---")

spark.sql("""
    SELECT MIN(salary) AS minimum_salary
    FROM employees
""").show()


# ============================================================
# 20.22 MAXIMUM SALARY
# ============================================================

print("\n--- Maximum Salary ---")

spark.sql("""
    SELECT MAX(salary) AS maximum_salary
    FROM employees
""").show()


# ============================================================
# 20.23 TOTAL SALARY
# ============================================================

print("\n--- Total Salary ---")

spark.sql("""
    SELECT SUM(salary) AS total_salary
    FROM employees
""").show()


# ============================================================
# 20.24 AVERAGE SALARY BY DEPARTMENT
# ============================================================

print("\n--- Average Salary by Department ---")

spark.sql("""
    SELECT
        department,
        AVG(salary) AS average_salary
    FROM employees
    GROUP BY department
""").show(truncate=False)


# ============================================================
# 20.25 EMPLOYEE COUNT BY DEPARTMENT
# ============================================================

print("\n--- Employee Count by Department ---")

spark.sql("""
    SELECT
        department,
        COUNT(*) AS employee_count
    FROM employees
    GROUP BY department
""").show(truncate=False)


# ============================================================
# 20.26 SORT ASCENDING
# ============================================================

print("\n--- Salary ASCENDING ---")

spark.sql("""
    SELECT *
    FROM employees
    ORDER BY salary ASC
""").show(truncate=False)


# ============================================================
# 20.27 SORT DESCENDING
# ============================================================

print("\n--- Salary DESCENDING ---")

spark.sql("""
    SELECT *
    FROM employees
    ORDER BY salary DESC
""").show(truncate=False)


# ============================================================
# 20.28 TOP 5 HIGHEST PAID EMPLOYEES
# ============================================================

print("\n--- Top 5 Highest Paid Employees ---")

spark.sql("""
    SELECT *
    FROM employees
    ORDER BY salary DESC
    LIMIT 5
""").show(truncate=False)


# ============================================================
# 20.29 EMPLOYEE WITH HIGHEST SALARY
# ============================================================

print("\n--- Highest Paid Employee ---")

spark.sql("""
    SELECT *
    FROM employees
    ORDER BY salary DESC
    LIMIT 1
""").show(truncate=False)


# ============================================================
# 20.30 FILTER + SELECT + SORT
# ============================================================

print("\n--- Salary > 7000, Sorted Highest First ---")

spark.sql("""
    SELECT name, department, salary
    FROM employees
    WHERE salary > 7000
    ORDER BY salary DESC
""").show(truncate=False)