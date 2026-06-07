import argparse
import json
from pathlib import Path

from pyspark.sql import SparkSession

from src.utils.config import load_config, resolve_paths
from src.utils.logger import get_logger
from src.utils.spark_session import create_spark_session


logger = get_logger(__name__)


def parquet_count(spark: SparkSession, path: str) -> int | None:
    if not Path(path).exists():
        return None
    return spark.read.parquet(path).count()


def collect_pipeline_metrics(spark: SparkSession, paths: dict[str, str]) -> dict[str, int | None]:
    return {
        "bronze_online_retail_rows": parquet_count(spark, paths["bronze_online_retail"]),
        "silver_sales_rows": parquet_count(spark, paths["silver_sales"]),
        "gold_dim_customer_rows": parquet_count(spark, paths["gold_dim_customer"]),
        "gold_dim_product_rows": parquet_count(spark, paths["gold_dim_product"]),
        "gold_dim_date_rows": parquet_count(spark, paths["gold_dim_date"]),
        "gold_fact_sales_rows": parquet_count(spark, paths["gold_fact_sales"]),
    }


def main(env: str = "dev") -> None:
    config = load_config(env)
    paths = resolve_paths(config)
    spark = create_spark_session(config["app"]["name"], config.get("spark"))
    metrics = collect_pipeline_metrics(spark, paths)
    logger.info("Pipeline metrics:\n%s", json.dumps(metrics, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect row-count metrics for pipeline outputs.")
    parser.add_argument("--env", default="dev", help="Config environment name.")
    args = parser.parse_args()
    main(args.env)
