from datetime import datetime

from src.transformations.build_fact_sales import build_fact_sales


def test_build_fact_sales_selects_business_keys_and_metrics(spark):
    sales_df = spark.createDataFrame(
        [
            ("536365", "85123A", "WHITE HEART", 6, datetime(2010, 12, 1, 8, 26), 2.55, 17850, "United Kingdom", 15.3),
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

    row = build_fact_sales(sales_df).first()

    assert row.sales_line_id
    assert row.date_key == 20101201
    assert row.invoice_no == "536365"
    assert row.customer_id == 17850
    assert row.stock_code == "85123A"
    assert row.sales_amount == 15.3
