import argparse

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, concat_ws, date_format, sha2, to_date

from src.utils.config import load_config, resolve_paths
from src.utils.logger import get_logger
from src.utils.spark_session import create_spark_session


logger = get_logger(__name__)


def build_fact_sales(sales_df: DataFrame) -> DataFrame:
    return (
        sales_df.withColumn(
            "sales_line_id",
            sha2(
                concat_ws(
                    "||",
                    col("invoice_no"),
                    col("stock_code"),
                    col("customer_id").cast("string"),
                    col("invoice_date").cast("string"),
                    col("quantity").cast("string"),
                    col("unit_price").cast("string"),
                ),
                256,
            ),
        )
        .withColumn("date_key", date_format(to_date("invoice_date"), "yyyyMMdd").cast("int"))
        .select(
            "sales_line_id",
            "invoice_no",
            "date_key",
            "customer_id",
            "stock_code",
            "quantity",
            "unit_price",
            "sales_amount",
            "country",
        )
    )


def main(env: str = "dev") -> None:
    config = load_config(env)
    paths = resolve_paths(config)
    spark = create_spark_session(config["app"]["name"], config.get("spark"))
    fact_df = build_fact_sales(spark.read.parquet(paths["silver_sales"]))
    fact_df.write.mode("overwrite").parquet(paths["gold_fact_sales"])
    logger.info("Sales fact created with %s rows", fact_df.count())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build sales fact table.")
    parser.add_argument("--env", default="dev", help="Config environment name.")
    args = parser.parse_args()
    main(args.env)
