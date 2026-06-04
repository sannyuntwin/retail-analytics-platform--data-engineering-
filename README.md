# Retail Analytics Platform

Local Spark analytics project for the Online Retail dataset. The pipeline follows a medallion layout:

- Bronze: raw Excel records converted to Parquet.
- Silver: cleaned, typed, deduplicated sales records.
- Gold: conformed customer, product, date, and sales fact tables.

## Project Layout

```text
configs/          Environment-specific runtime settings
data/             Local raw, bronze, silver, and gold storage
src/              Spark ingestion, transformation, quality, and utility code
sql/              Business analysis queries over gold tables
tests/            Pytest coverage for pipeline functions
docs/             Architecture and design notes
terraform/        Cloud deployment scaffold
dashboards/       Power BI and dashboard asset placeholders
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Place `OnlineRetail.xlsx` at `data/raw/OnlineRetail.xlsx`.

## Run Locally

```powershell
python -m src.ingestion.ingest_to_bronze --env dev
python -m src.transformations.clean_sales --env dev
python -m src.transformations.build_dim_customer --env dev
python -m src.transformations.build_dim_product --env dev
python -m src.transformations.build_dim_date --env dev
python -m src.transformations.build_fact_sales --env dev
python -m src.quality.data_validation --env dev
python -m src.monitoring.pipeline_metrics --env dev
```

## Test

```powershell
python -m pytest
```

# retail-analytics-platform--data-engineering-
