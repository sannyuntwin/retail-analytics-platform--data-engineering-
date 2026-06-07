import argparse
from dataclasses import dataclass

from pyspark.sql import DataFrame

from src.quality.quality_rules import QualityRule, sales_quality_rules
from src.utils.config import load_config, resolve_paths
from src.utils.logger import get_logger
from src.utils.spark_session import create_spark_session


logger = get_logger(__name__)


@dataclass(frozen=True)
class QualityResult:
    rule: str
    description: str
    failing_rows: int

    @property
    def passed(self) -> bool:
        return self.failing_rows == 0


def run_quality_checks(df: DataFrame, rules: list[QualityRule]) -> list[QualityResult]:
    return [
        QualityResult(rule.name, rule.description, rule.failing_count(df))
        for rule in rules
    ]


def assert_quality(results: list[QualityResult]) -> None:
    failures = [result for result in results if not result.passed]
    if failures:
        details = "; ".join(
            f"{failure.rule} failed for {failure.failing_rows} rows"
            for failure in failures
        )
        raise AssertionError(details)


def main(env: str = "dev") -> None:
    config = load_config(env)
    paths = resolve_paths(config)
    spark = create_spark_session(config["app"]["name"], config.get("spark"))
    sales_df = spark.read.parquet(paths["silver_sales"])
    results = run_quality_checks(sales_df, sales_quality_rules())

    for result in results:
        logger.info(
            "%s: %s (%s failing rows)",
            "PASS" if result.passed else "FAIL",
            result.rule,
            result.failing_rows,
        )

    assert_quality(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run silver sales quality checks.")
    parser.add_argument("--env", default="dev", help="Config environment name.")
    args = parser.parse_args()
    main(args.env)
