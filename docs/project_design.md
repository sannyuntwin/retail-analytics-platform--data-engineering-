# Project Design

## Objective

Build a local retail analytics platform that turns Online Retail transaction data into trustworthy business-ready tables.

## Architecture

1. Raw Excel data lands in `data/raw/OnlineRetail.xlsx`.
2. `src.ingestion.ingest_to_bronze` converts Excel rows to Parquet in `data/bronze/online_retail`.
3. `src.transformations.clean_sales` standardizes column names, types, and business filters in `data/silver/sales`.
4. Gold builders produce customer, product, date, and fact tables in `data/gold`.
5. Quality checks validate the silver layer before downstream use.
6. SQL files query the gold tables for dashboard and business metrics.

## Data Model

- `dim_customer`: one row per customer with country, order count, lifetime value, and first/last purchase timestamps.
- `dim_product`: one row per stock code with description, sold quantity, revenue, and invoice count.
- `dim_date`: one row per invoice date with calendar attributes.
- `fact_sales`: transaction line items keyed by customer, product, and date.

## Operational Notes

- Configuration is environment-based under `configs`.
- Paths are resolved from the repository root, so jobs can be run from any current working directory.
- Pipeline outputs are local Parquet directories and are ignored by Git.
- The `dashboards` and binary diagram paths are placeholders for exported Power BI and image assets.
