from src.transformations.clean_sales import clean_sales


def test_clean_sales_filters_invalid_rows_and_standardizes_columns(spark):
    raw_df = spark.createDataFrame(
        [
            ("536365", " 85123a ", " WHITE   HEART ", 6, "2010-12-01 08:26:00", 2.55, 17850.0, " United Kingdom "),
            ("C536366", "71053", "Returned item", 1, "2010-12-01 08:28:00", 3.39, 17850.0, "United Kingdom"),
            ("536367", "84406B", "No customer", 2, "2010-12-01 08:34:00", 1.45, None, "United Kingdom"),
            ("536368", "84029G", "Bad quantity", -1, "2010-12-01 08:34:00", 3.39, 13047.0, "United Kingdom"),
            ("536369", "22752", "Bad price", 1, "2010-12-01 08:35:00", 0.0, 13047.0, "United Kingdom"),
        ],
        ["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"],
    )

    rows = clean_sales(raw_df).collect()

    assert len(rows) == 1
    assert rows[0].invoice_no == "536365"
    assert rows[0].stock_code == "85123A"
    assert rows[0].description == "WHITE HEART"
    assert rows[0].customer_id == 17850
    assert rows[0].sales_amount == 15.3
