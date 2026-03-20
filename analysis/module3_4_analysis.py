import duckdb
import os

DATA_DIR = r"/Users/xiaoting/Desktop/EDHEC/职业规划/BA project/archive"

con = duckdb.connect()

con.execute(f"""
    CREATE VIEW orders AS 
    SELECT * FROM read_csv_auto('{DATA_DIR}/olist_orders_dataset.csv');
    CREATE VIEW order_items AS 
    SELECT * FROM read_csv_auto('{DATA_DIR}/olist_order_items_dataset.csv');
    CREATE VIEW order_payments AS 
    SELECT * FROM read_csv_auto('{DATA_DIR}/olist_order_payments_dataset.csv');
    CREATE VIEW customers AS 
    SELECT * FROM read_csv_auto('{DATA_DIR}/olist_customers_dataset.csv');
""")

# ── 模块三：转化漏斗分析 ──────────────────────────────────────
print("\n===== MODULE 3: Conversion Funnel =====")

funnel = con.execute("""
WITH funnel_stages AS (
    SELECT
        COUNT(*)                                              AS total_orders,
        COUNT(order_approved_at)                              AS approved,
        COUNT(order_delivered_carrier_date)                   AS shipped,
        COUNT(order_delivered_customer_date)                  AS delivered,
        COUNT(CASE WHEN order_status = 'canceled' 
                   THEN 1 END)                                AS canceled,
        -- 配送质量
        ROUND(AVG(CASE 
            WHEN order_delivered_customer_date IS NOT NULL
             AND order_estimated_delivery_date IS NOT NULL
            THEN DATEDIFF('day',
                 order_purchase_timestamp::TIMESTAMP,
                 order_delivered_customer_date::TIMESTAMP)
        END), 1)                                              AS avg_delivery_days,
        -- 超时率
        ROUND(AVG(CASE 
            WHEN order_delivered_customer_date > order_estimated_delivery_date 
            THEN 1.0 ELSE 0.0 
        END) * 100, 1)                                        AS late_delivery_pct
    FROM orders
)
SELECT
    total_orders,
    approved,
    shipped,
    delivered,
    canceled,
    -- 漏斗转化率
    ROUND(approved  * 100.0 / total_orders, 1) AS approval_rate_pct,
    ROUND(shipped   * 100.0 / approved,     1) AS ship_rate_pct,
    ROUND(delivered * 100.0 / shipped,      1) AS delivery_rate_pct,
    ROUND(canceled  * 100.0 / total_orders, 1) AS cancel_rate_pct,
    avg_delivery_days,
    late_delivery_pct
FROM funnel_stages
""").df()

print(funnel.to_string(index=False))
funnel.to_csv(os.path.join(DATA_DIR, "module3_funnel.csv"), index=False)


# ── 模块四：营收增长分解 ──────────────────────────────────────
print("\n===== MODULE 4: Revenue Attribution =====")

revenue = con.execute("""
WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        DATE_TRUNC('month', o.order_purchase_timestamp::TIMESTAMP) AS order_month,
        SUM(op.payment_value)  AS order_value,
        ROW_NUMBER() OVER (
            PARTITION BY c.customer_unique_id
            ORDER BY MIN(o.order_purchase_timestamp)
        )                      AS order_rank
    FROM orders o
    JOIN customers c       ON o.customer_id = c.customer_id
    JOIN order_payments op ON o.order_id = op.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id, order_month
)
SELECT
    order_month,
    ROUND(SUM(CASE WHEN order_rank = 1 
                   THEN order_value ELSE 0 END), 0)  AS new_customer_revenue,
    ROUND(SUM(CASE WHEN order_rank > 1 
                   THEN order_value ELSE 0 END), 0)  AS returning_customer_revenue,
    COUNT(DISTINCT CASE WHEN order_rank = 1 
                        THEN customer_unique_id END)  AS new_customers,
    COUNT(DISTINCT CASE WHEN order_rank > 1 
                        THEN customer_unique_id END)  AS returning_customers,
    ROUND(SUM(order_value), 0)                        AS total_revenue
FROM customer_orders
WHERE order_month BETWEEN '2017-01-01' AND '2018-08-31'
GROUP BY order_month
ORDER BY order_month
""").df()

print(revenue.to_string(index=False))
revenue.to_csv(os.path.join(DATA_DIR, "module4_revenue.csv"), index=False)

print("\n✅ 模块三、四完成，结果已保存")