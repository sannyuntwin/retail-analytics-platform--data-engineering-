import pandas as pd


EXPECTED_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]


def load_online_retail(path: str, sheet_name: str | int = 0) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
    missing_columns = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Online Retail file is missing required columns: {missing}")

    df["InvoiceNo"] = df["InvoiceNo"].astype(str)
    df["StockCode"] = df["StockCode"].astype(str)
    return df[EXPECTED_COLUMNS]
