import os
import sys

from pyspark.sql import SparkSession


def create_spark_session(app_name: str = "RetailAnalytics", config: dict | None = None) -> SparkSession:
    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)

    spark_config = config or {}
    builder = SparkSession.builder.appName(app_name).master(
        spark_config.get("master", "local[*]")
    )

    for key, value in spark_config.get("configs", {}).items():
        builder = builder.config(key, value)

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel(spark_config.get("log_level", "WARN"))
    return spark
