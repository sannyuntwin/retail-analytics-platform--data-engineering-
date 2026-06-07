SELECT
    stock_code,
    description,
    total_quantity_sold,
    total_revenue,
    invoice_count
FROM dim_product
ORDER BY total_revenue DESC
LIMIT 25;
