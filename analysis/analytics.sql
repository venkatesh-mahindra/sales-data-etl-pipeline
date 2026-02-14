-- ============================================
-- Sales Analytics SQL Queries
-- ============================================
-- This file contains comprehensive business analytics queries
-- for the sales data warehouse

-- ============================================
-- 1. TOP PRODUCTS BY REVENUE
-- ============================================
-- Query: Top 5 products by total revenue
SELECT 
    product,
    total_revenue,
    order_count,
    avg_price,
    unique_customers,
    revenue_per_unit
FROM product_summary
ORDER BY total_revenue DESC
LIMIT 5;

-- ============================================
-- 2. MONTHLY REVENUE TRENDS
-- ============================================
-- Query: Monthly revenue with growth metrics
SELECT 
    DATE_FORMAT(date, '%Y-%m') AS month,
    monthly_revenue,
    order_count,
    unique_customers,
    avg_order_value,
    ROUND(mom_growth * 100, 2) AS mom_growth_pct,
    ROUND(yoy_growth * 100, 2) AS yoy_growth_pct,
    revenue_trend
FROM monthly_sales_summary
ORDER BY date DESC
LIMIT 12;

-- ============================================
-- 3. STORE PERFORMANCE ANALYSIS
-- ============================================
-- Query: Best performing store locations
SELECT 
    store_location,
    region,
    COUNT(*) AS total_orders,
    SUM(total_price) AS total_revenue,
    AVG(total_price) AS avg_order_value,
    COUNT(DISTINCT customer_id) AS unique_customers,
    AVG(quantity) AS avg_quantity_per_order
FROM processed_sales
WHERE store_location IS NOT NULL
GROUP BY store_location, region
ORDER BY total_revenue DESC;

-- ============================================
-- 4. CUSTOMER SEGMENTATION ANALYSIS
-- ============================================
-- Query: Customer segments and their value
SELECT 
    customer_segment,
    COUNT(*) AS customer_count,
    SUM(monetary_value) AS total_revenue,
    AVG(monetary_value) AS avg_customer_value,
    AVG(frequency) AS avg_frequency,
    AVG(recency_days) AS avg_recency_days,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_summary), 2) AS segment_percentage
FROM customer_summary
GROUP BY customer_segment
ORDER BY total_revenue DESC;

-- ============================================
-- 5. REPEAT VS NEW CUSTOMER ANALYSIS
-- ============================================
-- Query: Compare repeat vs new customer performance
SELECT 
    CASE 
        WHEN order_count > 1 THEN 'Repeat Customer'
        ELSE 'New Customer'
    END AS customer_type,
    COUNT(*) AS customer_count,
    SUM(lifetime_value) AS total_revenue,
    AVG(lifetime_value) AS avg_customer_value,
    AVG(order_count) AS avg_orders_per_customer,
    AVG(customer_tenure_days) AS avg_tenure_days
FROM customer_summary
GROUP BY customer_type
ORDER BY total_revenue DESC;

-- ============================================
-- 6. PRODUCT CATEGORY PERFORMANCE
-- ============================================
-- Query: Performance by product category
SELECT 
    product_category,
    COUNT(*) AS total_orders,
    SUM(total_price) AS total_revenue,
    AVG(total_price) AS avg_order_value,
    SUM(quantity) AS total_quantity,
    AVG(price) AS avg_unit_price,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(total_price) * 100.0 / (SELECT SUM(total_price) FROM processed_sales), 2) AS revenue_share_pct
FROM processed_sales
GROUP BY product_category
ORDER BY total_revenue DESC;

-- ============================================
-- 7. REGIONAL PERFORMANCE ANALYSIS
-- ============================================
-- Query: Sales performance by region
SELECT 
    region,
    COUNT(*) AS total_orders,
    SUM(total_price) AS total_revenue,
    AVG(total_price) AS avg_order_value,
    COUNT(DISTINCT store_location) AS num_stores,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(quantity) AS total_quantity,
    ROUND(SUM(total_price) * 100.0 / (SELECT SUM(total_price) FROM processed_sales WHERE region IS NOT NULL), 2) AS revenue_share_pct
FROM processed_sales
WHERE region IS NOT NULL
GROUP BY region
ORDER BY total_revenue DESC;

-- ============================================
-- 8. TIME-BASED SALES PATTERNS
-- ============================================
-- Query: Sales patterns by weekday and weekend
SELECT 
    weekday_name,
    is_weekend,
    COUNT(*) AS total_orders,
    SUM(total_price) AS total_revenue,
    AVG(total_price) AS avg_order_value,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(total_price) * 100.0 / (SELECT SUM(total_price) FROM processed_sales), 2) AS revenue_share_pct
FROM processed_sales
GROUP BY weekday_name, is_weekend
ORDER BY is_weekend, weekday_name;

-- ============================================
-- 9. CUSTOMER LIFETIME VALUE ANALYSIS
-- ============================================
-- Query: Customer lifetime value distribution
SELECT 
    customer_tier,
    COUNT(*) AS customer_count,
    SUM(lifetime_value) AS total_revenue,
    AVG(lifetime_value) AS avg_lifetime_value,
    AVG(frequency) AS avg_purchase_frequency,
    AVG(customer_tenure_days) AS avg_tenure_days,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_summary), 2) AS tier_percentage
FROM customer_summary
GROUP BY customer_tier
ORDER BY avg_lifetime_value DESC;

-- ============================================
-- 10. CHURN RISK ANALYSIS
-- ============================================
-- Query: Customers at risk of churning
SELECT 
    churn_risk,
    COUNT(*) AS customer_count,
    SUM(monetary_value) AS total_revenue,
    AVG(monetary_value) AS avg_customer_value,
    AVG(days_since_last_order) AS avg_days_since_last,
    AVG(frequency) AS avg_historical_frequency,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_summary), 2) AS risk_percentage
FROM customer_summary
GROUP BY churn_risk
ORDER BY 
    CASE churn_risk 
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 3
    END;

-- ============================================
-- 11. SEASONAL SALES ANALYSIS
-- ============================================
-- Query: Seasonal sales patterns
SELECT 
    CASE 
        WHEN order_month IN (12, 1, 2) THEN 'Winter'
        WHEN order_month IN (3, 4, 5) THEN 'Spring'
        WHEN order_month IN (6, 7, 8) THEN 'Summer'
        WHEN order_month IN (9, 10, 11) THEN 'Fall'
    END AS season,
    COUNT(*) AS total_orders,
    SUM(total_price) AS total_revenue,
    AVG(total_price) AS avg_order_value,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(total_price) * 100.0 / (SELECT SUM(total_price) FROM processed_sales), 2) AS revenue_share_pct
FROM processed_sales
GROUP BY season
ORDER BY total_revenue DESC;

-- ============================================
-- 12. BULK ORDER ANALYSIS
-- ============================================
-- Query: Impact of bulk orders on business
SELECT 
    has_bulk_discount,
    COUNT(*) AS order_count,
    SUM(total_price) AS total_revenue,
    AVG(total_price) AS avg_order_value,
    SUM(quantity) AS total_quantity,
    AVG(quantity) AS avg_quantity_per_order,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(total_price) * 100.0 / (SELECT SUM(total_price) FROM processed_sales), 2) AS revenue_share_pct
FROM processed_sales
GROUP BY has_bulk_discount
ORDER BY total_revenue DESC;

-- ============================================
-- 13. REVENUE GROWTH ANALYSIS
-- ============================================
-- Query: Month-over-month revenue growth
SELECT 
    DATE_FORMAT(date, '%Y-%m') AS month,
    monthly_revenue,
    LAG(monthly_revenue) OVER (ORDER BY date) AS previous_month_revenue,
    ROUND(mom_growth * 100, 2) AS mom_growth_pct,
    revenue_trend,
    CASE 
        WHEN mom_growth > 0 THEN 'Growing'
        WHEN mom_growth < 0 THEN 'Declining'
        ELSE 'Stable'
    END AS growth_status
FROM monthly_sales_summary
ORDER BY date DESC
LIMIT 6;

-- ============================================
-- 14. HIGH-VALUE CUSTOMER ANALYSIS
-- ============================================
-- Query: High-value customer characteristics
SELECT 
    customer_id,
    monetary_value,
    frequency,
    recency_days,
    customer_segment,
    customer_tier,
    lifetime_value,
    avg_order_value,
    customer_tenure_days,
    unique_products,
    unique_stores
FROM customer_summary
WHERE monetary_value > 1000  -- High-value threshold
ORDER BY monetary_value DESC
LIMIT 20;

-- ============================================
-- 15. CROSS-SELLING OPPORTUNITIES
-- ============================================
-- Query: Product cross-selling analysis
WITH customer_products AS (
    SELECT 
        customer_id,
        product_category,
        COUNT(*) AS purchase_count
    FROM processed_sales
    GROUP BY customer_id, product_category
),
category_pairs AS (
    SELECT 
        cp1.product_category AS category_1,
        cp2.product_category AS category_2,
        COUNT(*) AS customer_count
    FROM customer_products cp1
    JOIN customer_products cp2 ON cp1.customer_id = cp2.customer_id
    WHERE cp1.product_category < cp2.product_category
    GROUP BY cp1.product_category, cp2.product_category
)
SELECT 
    category_1,
    category_2,
    customer_count,
    ROUND(customer_count * 100.0 / (SELECT COUNT(DISTINCT customer_id) FROM processed_sales), 2) AS customer_percentage
FROM category_pairs
ORDER BY customer_count DESC
LIMIT 10;

-- ============================================
-- 16. DAILY SALES PERFORMANCE
-- ============================================
-- Query: Daily sales performance metrics
SELECT 
    order_date,
    COUNT(*) AS daily_orders,
    SUM(total_price) AS daily_revenue,
    AVG(total_price) AS avg_order_value,
    COUNT(DISTINCT customer_id) AS daily_customers,
    SUM(quantity) AS daily_quantity,
    is_weekend,
    weekday_name
FROM processed_sales
GROUP BY order_date, is_weekend, weekday_name
ORDER BY order_date DESC
LIMIT 30;

-- ============================================
-- 17. PRICE SENSITIVITY ANALYSIS
-- ============================================
-- Query: Price category performance
SELECT 
    price_category,
    COUNT(*) AS order_count,
    SUM(total_price) AS total_revenue,
    AVG(total_price) AS avg_order_value,
    SUM(quantity) AS total_quantity,
    AVG(quantity) AS avg_quantity_per_order,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(total_price) * 100.0 / (SELECT SUM(total_price) FROM processed_sales), 2) AS revenue_share_pct
FROM processed_sales
GROUP BY price_category
ORDER BY total_revenue DESC;

-- ============================================
-- 18. ORDER SIZE DISTRIBUTION
-- ============================================
-- Query: Order size patterns
SELECT 
    order_size_category,
    COUNT(*) AS order_count,
    SUM(total_price) AS total_revenue,
    AVG(total_price) AS avg_order_value,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM processed_sales), 2) AS order_percentage
FROM processed_sales
GROUP BY order_size_category
ORDER BY total_revenue DESC;

-- ============================================
-- 19. DATA QUALITY REPORT
-- ============================================
-- Query: Data quality metrics
SELECT 
    'raw_sales' AS table_name,
    COUNT(*) AS total_records,
    COUNT(DISTINCT order_id) AS unique_orders,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT product) AS unique_products,
    MIN(order_date) AS earliest_date,
    MAX(order_date) AS latest_date,
    SUM(CASE WHEN price <= 0 THEN 1 ELSE 0 END) AS invalid_price_records,
    SUM(CASE WHEN quantity <= 0 THEN 1 ELSE 0 END) AS invalid_quantity_records
FROM raw_sales

UNION ALL

SELECT 
    'processed_sales' AS table_name,
    COUNT(*) AS total_records,
    COUNT(DISTINCT order_id) AS unique_orders,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT product) AS unique_products,
    MIN(order_date) AS earliest_date,
    MAX(order_date) AS latest_date,
    0 AS invalid_price_records,
    0 AS invalid_quantity_records
FROM processed_sales;

-- ============================================
-- 20. EXECUTIVE DASHBOARD SUMMARY
-- ============================================
-- Query: Executive summary metrics
SELECT 
    'Key Metrics' AS metric_category,
    metric_name,
    metric_value
FROM (
    SELECT 
        'Total Revenue' AS metric_name,
        CONCAT('$', FORMAT(SUM(total_price), 2)) AS metric_value
    FROM processed_sales
    
    UNION ALL
    
    SELECT 
        'Total Orders' AS metric_name,
        CAST(COUNT(*) AS CHAR) AS metric_value
    FROM processed_sales
    
    UNION ALL
    
    SELECT 
        'Total Customers' AS metric_name,
        CAST(COUNT(DISTINCT customer_id) AS CHAR) AS metric_value
    FROM processed_sales
    
    UNION ALL
    
    SELECT 
        'Average Order Value' AS metric_name,
        CONCAT('$', FORMAT(AVG(total_price), 2)) AS metric_value
    FROM processed_sales
    
    UNION ALL
    
    SELECT 
        'Top Product' AS metric_name,
        product AS metric_value
    FROM product_summary
    ORDER BY total_revenue DESC
    LIMIT 1
    
    UNION ALL
    
    SELECT 
        'Best Store Location' AS metric_name,
        store_location AS metric_value
    FROM (
        SELECT store_location, SUM(total_price) AS revenue
        FROM processed_sales
        WHERE store_location IS NOT NULL
        GROUP BY store_location
        ORDER BY revenue DESC
        LIMIT 1
    ) top_store
) metrics;
