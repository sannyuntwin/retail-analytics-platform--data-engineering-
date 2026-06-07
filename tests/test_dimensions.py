from datetime import datetime

from src.transformations.build_dim_customer import build_dim_customer
from src.transformations.build_dim_date import build_dim_date
from src.transformations.build_dim_product import build_dim_product


def test_build_dimensions_from_sales(spark):
    sales_df = spark.createDataFrame(
        [
            ("536365", "85123A", "WHITE HEART", 6, datetime(2010, 12, 1, 8, 26), 2.55, 17850, "United Kingdom", 15.3),
            ("536366", "71053", "WHITE METAL LANTERN", 6, datetime(2010, 12, 1, 8, 28), 3.39, 17850, "United Kingdom", 20.34),
            ("536367", "85123A", "WHITE HEART", 2, datetime(2010, 12, 2, 9, 10), 2.55, 13047, "United Kingdom", 5.1),
        ],
        [
            "invoice_no",
            "stock_code",
            "description",
            "quantity",
            "invoice_date",
            "unit_price",
            "customer_id",
            "country",
            "sales_amount",
        ],
    )

    customers = {row.customer_id: row for row in build_dim_customer(sales_df).collect()}
    products = {row.stock_code: row for row in build_dim_product(sales_df).collect()}
    dates = {row.date_key: row for row in build_dim_date(sales_df).collect()}

    assert customers[17850].order_count == 2
    assert customers[17850].lifetime_value == 35.64
    assert products["85123A"].total_quantity_sold == 8
    assert products["85123A"].total_revenue == 20.4
    assert set(dates) == {20101201, 20101202}
