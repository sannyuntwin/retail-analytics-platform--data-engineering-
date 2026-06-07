import argparse

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, regexp_replace, round as spark_round, to_timestamp, trim, upper

from src.utils.config import load_config, resolve_paths
from src.utils.logger import get_logger
from src.utils.spark_session import create_spark_session


logger = get_logger(__name__)


def clean_sales(df: DataFrame) -> DataFrame:
    renamed_df = (
        df.withColumnRenamed("InvoiceNo", "invoice_no")
        .withColumnRenamed("StockCode", "stock_code")
        .withColumnRenamed("Description", "description")
        .withColumnRenamed("Quantity", "quantity")
        .withColumnRenamed("InvoiceDate", "invoice_date")
        .withColumnRenamed("UnitPrice", "unit_price")
        .withColumnRenamed("CustomerID", "customer_id")
        .withColumnRenamed("Country", "country")
    )

    return (
        renamed_df.withColumn("invoice_no", trim(col("invoice_no").cast("string")))
        .withColumn("stock_code", upper(trim(col("stock_code").cast("string"))))
        .withColumn("description", regexp_replace(trim(col("description")), r"\s+", " "))
        .withColumn("quantity", col("quantity").cast("long"))
        .withColumn("invoice_date", to_timestamp(col("invoice_date")))
        .withColumn("unit_price", col("unit_price").cast("double"))
        .withColumn("customer_id", col("customer_id").cast("long"))
        .withColumn("country", trim(col("country")))
        .filter(col("customer_id").isNotNull())
        .filter(col("invoice_no").isNotNull())
        .filter(~upper(col("invoice_no")).startswith("C"))
        .filter(col("stock_code").isNotNull())
        .filter(col("description").isNotNull())
        .filter(col("quantity") > 0)
        .filter(col("unit_price") > 0)
        .withColumn("sales_amount", spark_round(col("quantity") * col("unit_price"), 2))
        .dropDuplicates(["invoice_no", "stock_code", "customer_id", "invoice_date", "quantity", "unit_price"])
    )


def write_silver_sales(df: DataFrame, silver_path: str) -> DataFrame:
    clean_df = clean_sales(df)
    clean_df.write.mode("overwrite").parquet(silver_path)
    return clean_df


def main(env: str = "dev") -> None:
    config = load_config(env)
    paths = resolve_paths(config)
    spark = create_spark_session(config["app"]["name"], config.get("spark"))
    bronze_df = spark.read.parquet(paths["bronze_online_retail"])
    row_count = write_silver_sales(bronze_df, paths["silver_sales"]).count()
    logger.info("Silver sales created with %s rows", row_count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean bronze records into silver sales.")
    parser.add_argument("--env", default="dev", help="Config environment name.")
    args = parser.parse_args()
    main(args.env)
