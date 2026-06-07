SELECT
    customer_id,
    country,
    order_count,
    lifetime_value,
    first_purchase_at,
    last_purchase_at
FROM dim_customer
ORDER BY lifetime_value DESC;
