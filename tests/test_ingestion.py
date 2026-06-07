import pandas as pd
import pytest

from src.ingestion.load_raw_data import EXPECTED_COLUMNS, load_online_retail


def test_load_online_retail_returns_expected_columns(tmp_path):
    source_path = tmp_path / "online_retail.xlsx"
    source_df = pd.DataFrame(
        [
            {
                "InvoiceNo": "536365",
                "StockCode": "85123A",
                "Description": "WHITE HANGING HEART T-LIGHT HOLDER",
                "Quantity": 6,
                "InvoiceDate": "2010-12-01 08:26:00",
                "UnitPrice": 2.55,
                "CustomerID": 17850,
                "Country": "United Kingdom",
                "Unused": "ignored",
            }
        ]
    )
    source_df.to_excel(source_path, index=False)

    loaded_df = load_online_retail(str(source_path))

    assert list(loaded_df.columns) == EXPECTED_COLUMNS
    assert loaded_df.iloc[0]["InvoiceNo"] == "536365"


def test_load_online_retail_rejects_missing_required_columns(tmp_path):
    source_path = tmp_path / "bad_online_retail.xlsx"
    pd.DataFrame([{"InvoiceNo": "536365"}]).to_excel(source_path, index=False)

    with pytest.raises(ValueError, match="missing required columns"):
        load_online_retail(str(source_path))
