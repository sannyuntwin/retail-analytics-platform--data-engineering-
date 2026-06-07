from dataclasses import dataclass
from typing import Callable

from pyspark.sql import DataFrame


@dataclass(frozen=True)
class QualityRule:
    name: str
    description: str
    failing_count: Callable[[DataFrame], int]


def sales_quality_rules() -> list[QualityRule]:
    return [
        QualityRule(
            "customer_id_not_null",
            "Silver sales must have a customer_id.",
            lambda df: df.filter("customer_id IS NULL").count(),
        ),
        QualityRule(
            "positive_quantity",
            "Silver sales must have positive quantity.",
            lambda df: df.filter("quantity <= 0 OR quantity IS NULL").count(),
        ),
        QualityRule(
            "positive_unit_price",
            "Silver sales must have positive unit_price.",
            lambda df: df.filter("unit_price <= 0 OR unit_price IS NULL").count(),
        ),
        QualityRule(
            "sales_amount_matches",
            "Sales amount must equal quantity multiplied by unit_price.",
            lambda df: df.filter("abs(sales_amount - round(quantity * unit_price, 2)) > 0.01").count(),
        ),
    ]
