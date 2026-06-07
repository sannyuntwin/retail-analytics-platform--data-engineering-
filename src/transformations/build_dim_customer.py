import argparse

from pyspark.sql import DataFrame
from pyspark.sql.functions import countDistinct, first, max as spark_max, min as spark_min, round as spark_round, sum as spark_sum

from src.utils.config import load_config, resolve_paths
from src.utils.logger import get_logger
from src.utils.spark_session import create_spark_session


logger = get_logger(__name__)


def build_dim_customer(sales_df: DataFrame) -> DataFrame:
    return (
        sales_df.groupBy("customer_id")
        .agg(
            first("country", ignorenulls=True).alias("country"),
            countDistinct("invoice_no").alias("order_count"),
            spark_round(spark_sum("sales_amount"), 2).alias("lifetime_value"),
            spark_min("invoice_date").alias("first_purchase_at"),
            spark_max("invoice_date").alias("last_purchase_at"),
        )
        .orderBy("customer_id")
    )


def main(env: str = "dev") -> None:
    config = load_config(env)
    paths = resolve_paths(config)
    spark = create_spark_session(config["app"]["name"], config.get("spark"))
    dim_df = build_dim_customer(spark.read.parquet(paths["silver_sales"]))
    dim_df.write.mode("overwrite").parquet(paths["gold_dim_customer"])
    logger.info("Customer dimension created with %s rows", dim_df.count())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build customer dimension.")
    parser.add_argument("--env", default="dev", help="Config environment name.")
    args = parser.parse_args()
    main(args.env)
