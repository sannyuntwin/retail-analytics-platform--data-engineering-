import argparse

from pyspark.sql import DataFrame
from pyspark.sql.functions import countDistinct, first, round as spark_round, sum as spark_sum

from src.utils.config import load_config, resolve_paths
from src.utils.logger import get_logger
from src.utils.spark_session import create_spark_session


logger = get_logger(__name__)


def build_dim_product(sales_df: DataFrame) -> DataFrame:
    return (
        sales_df.groupBy("stock_code")
        .agg(
            first("description", ignorenulls=True).alias("description"),
            spark_sum("quantity").alias("total_quantity_sold"),
            spark_round(spark_sum("sales_amount"), 2).alias("total_revenue"),
            countDistinct("invoice_no").alias("invoice_count"),
        )
        .orderBy("stock_code")
    )


def main(env: str = "dev") -> None:
    config = load_config(env)
    paths = resolve_paths(config)
    spark = create_spark_session(config["app"]["name"], config.get("spark"))
    dim_df = build_dim_product(spark.read.parquet(paths["silver_sales"]))
    dim_df.write.mode("overwrite").parquet(paths["gold_dim_product"])
    logger.info("Product dimension created with %s rows", dim_df.count())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build product dimension.")
    parser.add_argument("--env", default="dev", help="Config environment name.")
    args = parser.parse_args()
    main(args.env)
