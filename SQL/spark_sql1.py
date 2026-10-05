# %%
from pyspark.sql import SparkSession
# %%
spark = SparkSession.builder \
    .appName("CSV Data Analysis") \
    .master("local[*]") \
    .getOrCreate()

print("Spark Session Started")
# %%
spark = SparkSession.builder \
    .appName("CSV Data Analysis") \
    .master("local[*]") \
    .getOrCreate()

print("Spark Session Started")
# %%
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
customers_df.show()
# %%
orders_df.show()
# %%
products_df.show()
# %%
customers_df.createOrReplaceTempView("customers_temp")
orders_df.createOrReplaceTempView("orders_temp")
products_df.createOrReplaceTempView("products_temp")

print("Temporary views created")
# %%
spark.sql("""
    SELECT *
    FROM customers_temp
""").show()
# %% 
# QUERY 1: Total Sales Per Customer

spark.sql("""
    SELECT
        customer_id,
        SUM(sales_amount) AS total_sales
    FROM orders_temp
    GROUP BY customer_id
    ORDER BY total_sales DESC
""").show()
# %%
# QUERY 2: Total Quantity Sold Per Product

spark.sql("""
    SELECT
        product_id,
        SUM(quantity) AS total_quantity_sold
    FROM orders_temp
    GROUP BY product_id
    ORDER BY total_quantity_sold DESC
""").show()
# %%
# QUERY 3: Average Product Price Per Category

spark.sql("""
    SELECT
        category,
        AVG(price) AS average_product_price
    FROM products_temp
    GROUP BY category
    ORDER BY average_product_price DESC
""").show()
# %%
# QUERY 4: Top 5 Most Expensive Products

spark.sql("""
    SELECT
        product_id,
        product_name,
        category,
        price
    FROM products_temp
    ORDER BY price DESC
    LIMIT 5
""").show()
# %%
# QUERY 5: Order Details With Customer and Product Name

spark.sql("""
    SELECT
        o.order_id,
        o.order_date,
        o.quantity,
        o.unit_price,
        o.sales_amount,
        o.order_status,
        c.customer_name,
        p.product_name
    FROM orders_temp o
    JOIN customers_temp c
        ON o.customer_id = c.customer_id
    JOIN products_temp p
        ON o.product_id = p.product_id
""").show()

# %%
# QUERY 6: Top 3 Customers Based on Total Spending

spark.sql("""
    SELECT
        c.customer_id,
        c.customer_name,
        c.city,
        c.membership_type,
        SUM(o.sales_amount) AS total_spending
    FROM customers_temp c
    JOIN orders_temp o
        ON c.customer_id = o.customer_id
    JOIN products_temp p
        ON o.product_id = p.product_id
    GROUP BY
        c.customer_id,
        c.customer_name,
        c.city,
        c.membership_type
    ORDER BY total_spending DESC
    LIMIT 3
""").show()

# %%
# QUERY 7: Number of Orders Placed by Each Membership Type

spark.sql("""
    SELECT
        c.membership_type,
        COUNT(o.order_id) AS total_orders
    FROM customers_temp c
    JOIN orders_temp o
        ON c.customer_id = o.customer_id
    GROUP BY c.membership_type
    ORDER BY total_orders DESC
""").show()
# %%
# QUERY 8: Customers Who Have Not Placed Any Orders

spark.sql("""
    SELECT
        c.customer_id,
        c.customer_name,
        c.city,
        c.membership_type
    FROM customers_temp c
    LEFT ANTI JOIN orders_temp o
        ON c.customer_id = o.customer_id
""").show()

# %%
# QUERY 9: Number of Orders and Total Spending for Each City

spark.sql("""
    SELECT
        c.city,
        COUNT(o.order_id) AS total_orders,
        SUM(o.sales_amount) AS total_spending
    FROM customers_temp c
    JOIN orders_temp o
        ON c.customer_id = o.customer_id
    GROUP BY c.city
    ORDER BY total_spending DESC
""").show()

# %%
# QUERY 10: Products That Have Never Been Ordered

spark.sql("""
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.price
    FROM products_temp p
    LEFT ANTI JOIN orders_temp o
        ON p.product_id = o.product_id
""").show()
# %%
# QUERY 12: Number of Days Between Order Date and Ship Date

spark.sql("""
    SELECT
        order_id,
        order_date,
        ship_date,
        DATEDIFF(ship_date, order_date) AS days_between
    FROM orders_temp
""").show()

# %%
# QUERY 11: Top 3 Products in Each Category Based on Sales

spark.sql("""
    SELECT
        category,
        product_id,
        product_name,
        total_sales,
        sales_rank
    FROM (
        SELECT
            p.category,
            p.product_id,
            p.product_name,
            SUM(o.sales_amount) AS total_sales,
            RANK() OVER (
                PARTITION BY p.category
                ORDER BY SUM(o.sales_amount) DESC
            ) AS sales_rank
        FROM products_temp p
        JOIN orders_temp o
            ON p.product_id = o.product_id
        GROUP BY
            p.category,
            p.product_id,
            p.product_name
    ) ranked_products
    WHERE sales_rank <= 3
    ORDER BY category, sales_rank
""").show()
# %%
