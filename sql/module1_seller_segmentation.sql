-- ============================================================
-- Module 1: Seller Segmentation & Performance Scoring
-- Business Question: Which sellers are core assets vs at-risk?
-- ============================================================

-- Step 1: Base metrics per seller
SELECT 
    oi.seller_id,
    COUNT(DISTINCT oi.order_id)          AS total_orders,
    ROUND(SUM(oi.price), 2)              AS total_revenue,
    ROUND(AVG(oi.price), 2)              AS avg_order_value,
    ROUND(AVG(r.review_score), 2)        AS avg_review_score,
    COUNT(DISTINCT o.customer_id)        AS unique_customers
FROM order_items oi
JOIN orders o       ON oi.order_id = o.order_id
JOIN order_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY oi.seller_id
HAVING total_orders >= 5
ORDER BY total_revenue DESC
LIMIT 20;

-- Step 2: Quartile scoring
WITH seller_metrics AS (
    SELECT 
        oi.seller_id,
        COUNT(DISTINCT oi.order_id)          AS total_orders,
        ROUND(SUM(oi.price), 2)              AS total_revenue,
        ROUND(AVG(oi.price), 2)              AS avg_order_value,
        ROUND(AVG(r.review_score), 2)        AS avg_review_score,
        COUNT(DISTINCT o.customer_id)        AS unique_customers
    FROM order_items oi
    JOIN orders o        ON oi.order_id = o.order_id
    JOIN order_reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY oi.seller_id
    HAVING total_orders >= 5
),
scored AS (
    SELECT *,
        NTILE(4) OVER (ORDER BY total_revenue)    AS revenue_q,
        NTILE(4) OVER (ORDER BY total_orders)     AS volume_q,
        NTILE(4) OVER (ORDER BY avg_review_score) AS quality_q
    FROM seller_metrics
)
SELECT *,
    (revenue_q + volume_q + quality_q) AS composite_score
FROM scored
ORDER BY composite_score DESC
LIMIT 20;

-- Step 3: Final tiering model + summary
WITH seller_metrics AS (
    SELECT 
        oi.seller_id,
        s.seller_city,
        s.seller_state,
        COUNT(DISTINCT oi.order_id)          AS total_orders,
        ROUND(SUM(oi.price), 2)              AS total_revenue,
        ROUND(AVG(oi.price), 2)              AS avg_order_value,
        ROUND(AVG(r.review_score), 2)        AS avg_review_score,
        COUNT(DISTINCT o.customer_id)        AS unique_customers
    FROM order_items oi
    JOIN orders o        ON oi.order_id = o.order_id
    JOIN order_reviews r ON o.order_id = r.order_id
    JOIN sellers s       ON oi.seller_id = s.seller_id
    WHERE o.order_status = 'delivered'
    GROUP BY oi.seller_id, s.seller_city, s.seller_state
    HAVING total_orders >= 5
),
scored AS (
    SELECT *,
        NTILE(4) OVER (ORDER BY total_revenue)    AS revenue_q,
        NTILE(4) OVER (ORDER BY total_orders)     AS volume_q,
        NTILE(4) OVER (ORDER BY avg_review_score) AS quality_q
    FROM seller_metrics
),
tiered AS (
    SELECT *,
        (revenue_q + volume_q + quality_q) AS composite_score,
        CASE 
            WHEN (revenue_q + volume_q + quality_q) >= 10 THEN 'Tier 1 - Star'
            WHEN (revenue_q + volume_q + quality_q) >= 7  THEN 'Tier 2 - Growth'
            WHEN (revenue_q + volume_q + quality_q) >= 4  THEN 'Tier 3 - Average'
            ELSE                                               'Tier 4 - At Risk'
        END AS seller_tier
    FROM scored
)
SELECT * FROM tiered
ORDER BY composite_score DESC;