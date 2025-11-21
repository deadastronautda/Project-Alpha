import pandas as pd
from app import (
    load_data,
    preprocess_data,
    calculate_financial_ratios,
    perform_horizontal_analysis,
    perform_vertical_analysis,
    detect_anomalies
)

def test_load_data(loaded_df):
    assert "Показатель" in loaded_df.columns
    assert "Код" in loaded_df.columns
    assert "Год" in loaded_df.columns
    assert "Значение" in loaded_df.columns

def test_preprocess_data(preprocessed_df):
    assert "Показатель" in preprocessed_df.columns
    assert len(preprocessed_df.columns) > 3

def test_horizontal_analysis(preprocessed_df):
    df = perform_horizontal_analysis(preprocessed_df)
    assert not df.empty
    assert any("%" in c for c in df.columns)

def test_vertical_analysis(preprocessed_df):
    df = perform_vertical_analysis(preprocessed_df)
    assert not df.empty
    assert any("%" in c for c in df.columns)

def test_financial_ratios(preprocessed_df):
    ratios = calculate_financial_ratios(preprocessed_df)
    assert "Год" in ratios.columns
    assert len(ratios) >= 1

def test_anomalies(preprocessed_df):
    anomalies = detect_anomalies(preprocessed_df)
    assert isinstance(anomalies, list)