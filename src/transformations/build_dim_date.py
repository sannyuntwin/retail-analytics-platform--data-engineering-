import argparse

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, date_format, dayofmonth, dayofweek, quarter, to_date, weekofyear, year, month

from src.utils.config import load_config, resolve_paths
from src.utils.logger import get_logger
from src.utils.spark_session import create_spark_session


logger = get_logger(__name__)


def build_dim_date(sales_df: DataFrame) -> DataFrame:
    return (
        sales_df.select(to_date("invoice_date").alias("date"))
        .where(col("date").isNotNull())
        .dropDuplicates(["date"])
        .withColumn("date_key", date_format("date", "yyyyMMdd").cast("int"))
        .withColumn("year", year("date"))
        .withColumn("quarter", quarter("date"))
        .withColumn("month", month("date"))
        .withColumn("day", dayofmonth("date"))
        .withColumn("day_of_week", dayofweek("date"))
        .withColumn("week_of_year", weekofyear("date"))
        .select("date_key", "date", "year", "quarter", "month", "day", "day_of_week", "week_of_year")
        .orderBy("date_key")
    )


def main(env: str = "dev") -> None:
    config = load_config(env)
    paths = resolve_paths(config)
    spark = create_spark_session(config["app"]["name"], config.get("spark"))
    dim_df = build_dim_date(spark.read.parquet(paths["silver_sales"]))
    dim_df.write.mode("overwrite").parquet(paths["gold_dim_date"])
    logger.info("Date dimension created with %s rows", dim_df.count())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build date dimension.")
    parser.add_argument("--env", default="dev", help="Config environment name.")
    args = parser.parse_args()
    main(args.env)
