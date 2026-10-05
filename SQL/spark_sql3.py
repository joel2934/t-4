# %%
# CREATE SPARK SESSION

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("PySpark Practice") \
    .master("local[*]") \
    .getOrCreate()

print("Spark Session Started")
# %%
# READ CSV FILES

customers_df = spark.read.csv(
    "customers_dataset.csv",
    header=True,
    inferSchema=True
)

orders_df = spark.read.csv(
    "orders_dataset.csv",
    header=True,
    inferSchema=True
)

products_df = spark.read.csv(
    "products_dataset.csv",
    header=True,
    inferSchema=True
)
# %%
# CREATE TEMPORARY VIEWS

customers_df.createOrReplaceTempView("customers_temp")

orders_df.createOrReplaceTempView("orders_temp")

products_df.createOrReplaceTempView("products_temp")
# %%
# CHECK DATA

customers_df.show()
orders_df.show()
products_df.show()

# %%
# CHECK SCHEMAS

customers_df.printSchema()
orders_df.printSchema()
products_df.printSchema()
# %%
# QUERY 1: Top 10 Revenue Generating Customers
spark.sql("""
    SELECT
        c.customer_name,
        c.customer_id,
        SUM(o.sales_amount) AS total_revenue
        FROM customers_temp c
        JOIN orders_temp o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.customer_name
        ORDER BY total_revenue DESC
        LIMIT 10
""").show()


# %%
# QUERY 2: Monthly Revenue Trend

spark.sql("""
    SELECT
        DATE_FORMAT(order_date, 'yyyy-MM') AS month,
        SUM(sales_amount) AS total_revenue
    FROM orders_temp
    GROUP BY DATE_FORMAT(order_date, 'yyyy-MM')
    ORDER BY month
""").show()
# %%
# QUERY 3: Running Total Revenue

spark.sql("""
    SELECT
        order_date,
        SUM(sales_amount) AS daily_revenue,
        SUM(SUM(sales_amount)) OVER (
            ORDER BY order_date
        ) AS running_total_revenue
    FROM orders_temp
    GROUP BY order_date
    ORDER BY order_date
""").show()

# %%
# QUERY 4: Previous Order Analysis

spark.sql("""
    SELECT
        customer_id,
        order_date,
        sales_amount,
        LAG(sales_amount) OVER (
            PARTITION BY customer_id
            ORDER BY order_date
        ) AS previous_purchase_amount
    FROM orders_temp
    ORDER BY customer_id, order_date
""").show()
# %%
# QUERY 5: Next Purchase Prediction Using LEAD

spark.sql("""
    SELECT
        customer_id,
        order_date,
        sales_amount,
        LEAD(sales_amount) OVER (
            PARTITION BY customer_id
            ORDER BY order_date
        ) AS next_purchase_amount
    FROM orders_temp
    ORDER BY customer_id, order_date
""").show()

# %%
# QUERY 8: Average Shipping Delay

spark.sql("""
    SELECT
        AVG(DATEDIFF(ship_date, order_date)) AS average_shipping_delay
    FROM orders_temp
""").show()

# %%
# QUERY 9: Customers With No Orders

spark.sql("""
    SELECT
        c.customer_id,
        c.customer_name
    FROM customers_temp c
    LEFT ANTI JOIN orders_temp o
        ON c.customer_id = o.customer_id
""").show()

# %%
# QUERY 11: Detect Revenue Drop

spark.sql("""
    SELECT
        customer_id,
        order_date,
        sales_amount,
        previous_sales
    FROM (
        SELECT
            customer_id,
            order_date,
            sales_amount,
            LAG(sales_amount) OVER (
                PARTITION BY customer_id
                ORDER BY order_date
            ) AS previous_sales
        FROM orders_temp
    ) t
    WHERE sales_amount < previous_sales
""").show()
# %%
# QUERY 12: Day-wise Revenue Analysis

spark.sql("""
    SELECT
        date_format(order_date, 'EEEE') AS day_name,
        SUM(sales_amount) AS total_revenue
    FROM orders_temp
    GROUP BY date_format(order_date, 'EEEE')
    ORDER BY total_revenue DESC
""").show()
# %%
# QUERY 13: 7-Day Moving Average Sales

spark.sql("""
    SELECT
        order_date,
        SUM(sales_amount) AS daily_sales,
        AVG(SUM(sales_amount)) OVER (
            ORDER BY order_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS moving_average
    FROM orders_temp
    GROUP BY order_date
    ORDER BY order_date
""").show()
# %%
# QUERY 18: Peak Sales Hour Analysis

spark.sql("""
    SELECT
        HOUR(order_date) AS sales_hour,
        COUNT(*) AS total_orders
    FROM orders_temp
    GROUP BY HOUR(order_date)
    ORDER BY total_orders DESC
    LIMIT 1
""").show()

# %%
# QUERY 16: Customer Churn Prediction Logic

spark.sql("""
    SELECT
        c.customer_id,
        c.customer_name,
        MAX(o.order_date) AS last_order_date
    FROM customers_temp c
    LEFT JOIN orders_temp o
        ON c.customer_id = o.customer_id
    GROUP BY
        c.customer_id,
        c.customer_name
    HAVING
        MAX(o.order_date) < DATE_SUB(CURRENT_DATE(), 90)
        OR MAX(o.order_date) IS NULL
""").show()
# %%
# QUERY 17: Product Affinity Analysis

spark.sql("""
    SELECT
        o1.product_id AS product_1,
        o2.product_id AS product_2,
        COUNT(*) AS times_bought_together
    FROM orders_temp o1
    JOIN orders_temp o2
        ON o1.customer_id = o2.customer_id
        AND o1.product_id < o2.product_id
    GROUP BY
        o1.product_id,
        o2.product_id
    ORDER BY times_bought_together DESC
""").show()

# %%
# QUERY 18: Peak Sales Hour Analysis

spark.sql("""
    SELECT
        HOUR(order_date) AS sales_hour,
        COUNT(*) AS total_orders
    FROM orders_temp
    GROUP BY HOUR(order_date)
    ORDER BY total_orders DESC
    LIMIT 1
""").show()
# %%
# QUERY 19: Inventory Risk Detection

spark.sql("""
    SELECT
        p.product_id,
        p.product_name,
        p.stock_quantity,
        SUM(o.quantity) AS total_quantity_sold
    FROM products_temp p
    JOIN orders_temp o
        ON p.product_id = o.product_id
    GROUP BY
        p.product_id,
        p.product_name,
        p.stock_quantity
    HAVING
        p.stock_quantity < SUM(o.quantity)
    ORDER BY p.stock_quantity
""").show()