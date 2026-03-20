import duckdb
import os


DATA_DIR = r"/Users/xiaoting/Desktop/EDHEC/职业规划/BA project/archive"

con = duckdb.connect()

con.execute(f"""
    CREATE VIEW orders AS 
    SELECT * FROM read_csv_auto('{DATA_DIR}/olist_orders_dataset.csv');
    
    CREATE VIEW customers AS 
    SELECT * FROM read_csv_auto('{DATA_DIR}/olist_customers_dataset.csv');
    
    CREATE VIEW order_items AS 
    SELECT * FROM read_csv_auto('{DATA_DIR}/olist_order_items_dataset.csv');
    
    CREATE VIEW order_payments AS 
    SELECT * FROM read_csv_auto('{DATA_DIR}/olist_order_payments_dataset.csv');
    
    CREATE VIEW order_reviews AS 
    SELECT * FROM read_csv_auto('{DATA_DIR}/olist_order_reviews_dataset.csv');
    
    CREATE VIEW sellers AS 
    SELECT * FROM read_csv_auto('{DATA_DIR}/olist_sellers_dataset.csv');
    
    CREATE VIEW products AS 
    SELECT * FROM read_csv_auto('{DATA_DIR}/olist_products_dataset.csv');
""")

print("✅ Data loaded, starting cohort query...")

result = con.execute("""
WITH base AS (
    SELECT
        c.customer_unique_id,
        DATE_TRUNC('month', o.order_purchase_timestamp::TIMESTAMP) AS order_month,
        COALESCE(op.payment_value, 0) AS payment_value
    FROM orders o
    JOIN customers c       ON o.customer_id = c.customer_id
    JOIN order_payments op ON o.order_id = op.order_id
    WHERE o.order_status = 'delivered'
),
cohort_def AS (
    SELECT
        customer_unique_id,
        MIN(order_month) AS cohort_month
    FROM base
    GROUP BY customer_unique_id
),
cohort_activity AS (
    SELECT
        cd.cohort_month,
        b.order_month,
        DATEDIFF('month', cd.cohort_month, b.order_month) AS month_offset,
        b.customer_unique_id,
        b.payment_value
    FROM base b
    JOIN cohort_def cd ON b.customer_unique_id = cd.customer_unique_id
    WHERE cd.cohort_month BETWEEN '2017-01-01' AND '2018-06-30'
),
cohort_stats AS (
    SELECT
        cohort_month,
        month_offset,
        COUNT(DISTINCT customer_unique_id) AS active_users,
        ROUND(SUM(payment_value), 2)       AS cohort_revenue
    FROM cohort_activity
    GROUP BY cohort_month, month_offset
),
cohort_size AS (
    SELECT cohort_month, active_users AS initial_size
    FROM cohort_stats
    WHERE month_offset = 0
)
SELECT
    st.month_offset,
    ROUND(AVG(st.active_users * 100.0 / cs.initial_size), 1) AS avg_retention_rate,
    ROUND(AVG(st.cohort_revenue / cs.initial_size), 2)        AS avg_revenue_per_user
FROM cohort_stats st
JOIN cohort_size cs ON st.cohort_month = cs.cohort_month
GROUP BY st.month_offset
ORDER BY st.month_offset
LIMIT 13
""").df()

print(result)

# Save results
output_path = os.path.join(DATA_DIR, "module2_cohort_summary.csv")
result.to_csv(output_path, index=False)
print(f"\n✅ Results saved to: {output_path}")