import argparse

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import current_timestamp, input_file_name, lit

from src.ingestion.load_raw_data import load_online_retail
from src.utils.config import load_config, resolve_paths
from src.utils.logger import get_logger
from src.utils.spark_session import create_spark_session


logger = get_logger(__name__)


def ingest_to_bronze(spark: SparkSession, raw_file_path: str, bronze_path: str) -> DataFrame:
    pdf = load_online_retail(raw_file_path)
    bronze_df = (
        spark.createDataFrame(pdf)
        .withColumn("ingested_at", current_timestamp())
        .withColumn("source_file", lit(raw_file_path))
    )
    bronze_df.write.mode("overwrite").parquet(bronze_path)
    return bronze_df


def main(env: str = "dev") -> None:
    config = load_config(env)
    paths = resolve_paths(config)
    spark = create_spark_session(config["app"]["name"], config.get("spark"))
    row_count = ingest_to_bronze(
        spark,
        paths["raw_file"],
        paths["bronze_online_retail"],
    ).count()
    logger.info("Bronze ingestion completed with %s rows", row_count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest Online Retail Excel data to bronze.")
    parser.add_argument("--env", default="dev", help="Config environment name.")
    args = parser.parse_args()
    main(args.env)
