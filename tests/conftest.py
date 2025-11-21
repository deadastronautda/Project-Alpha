import pytest
import pandas as pd
from pathlib import Path

from tests.data_loader import load_data, preprocess_data
from tests.financial_analyzer import calculate_financial_ratios
from tests.anomaly_detector import detect_anomalies

@pytest.fixture(scope="session")
def excel_path():
    """Путь к реальному файлу отчетности"""
    return Path(__file__).parent.parent / "financial_data_flat.xlsx"

@pytest.fixture(scope="session")
def loaded_df(excel_path):
    df = load_data(excel_path)
    assert not df.empty
    return df

@pytest.fixture(scope="session")
def preprocessed_df(loaded_df):
    df = preprocess_data(loaded_df)
    assert not df.empty
    return df