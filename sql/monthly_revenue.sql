SELECT
    d.year,
    d.month,
    ROUND(SUM(f.sales_amount), 2) AS revenue,
    COUNT(DISTINCT f.invoice_no) AS orders
FROM fact_sales f
JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;
