# %%
# CREATE SPARK SESSION

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Log Analysis") \
    .master("local[*]") \
    .getOrCreate()

print("Spark Session Started")
# %%
# READ AND PARSE LOG FILE

from pyspark.sql.functions import split, col

logs_df = spark.read.text("app_logs.txt")

logs_df = logs_df.select(
    split(col("value"), " ").getItem(0).alias("date"),
    split(col("value"), " ").getItem(1).alias("time"),
    split(col("value"), " ").getItem(2).alias("log_level"),
    split(col("value"), " ").getItem(3).alias("user"),
    split(col("value"), " ").getItem(4).alias("action"),
    split(col("value"), " ").getItem(5).alias("detail")
)

logs_df.createOrReplaceTempView("logs_temp")

logs_df.show()

# %%
# QUERY 1: Count of Each Log Level

spark.sql("""
    SELECT
        log_level,
        COUNT(*) AS total_count
    FROM logs_temp
    GROUP BY log_level
    ORDER BY total_count DESC
""").show()
# %%
# QUERY 2: Most Active User

spark.sql("""
    SELECT
        user,
        COUNT(*) AS activity_count
    FROM logs_temp
    GROUP BY user
    ORDER BY activity_count DESC
    LIMIT 1
""").show()
# %%
# %%
# QUERY 3: Failed Login Attempts

spark.sql("""
    SELECT
        user,
        COUNT(*) AS failed_login_attempts
    FROM logs_temp
    WHERE action = 'login'
      AND detail = 'failed'
    GROUP BY user
    ORDER BY failed_login_attempts DESC
""").show()
# %%
