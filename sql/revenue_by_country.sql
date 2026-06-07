SELECT
    country,
    ROUND(SUM(sales_amount), 2) AS revenue,
    COUNT(DISTINCT invoice_no) AS orders,
    COUNT(DISTINCT customer_id) AS customers
FROM fact_sales
GROUP BY country
ORDER BY revenue DESC;
