import pytest
import pandas as pd
from io import BytesIO
from app import *

def test_clean_value():
    """Тестирует очистку числовых значений"""
    assert clean_value("1,146") == 1.146
    assert clean_value("395,544") == 395.544
    assert clean_value("0") == 0.0
    assert clean_value("") is None
    assert clean_value("-") is None
    assert clean_value("н/д") is None
    assert clean_value("123.45") == 123.45
    assert clean_value("123,45") == 123.45

def test_detect_financial_table_start():
    """Тестирует определение начала финансовой отчетности"""
    # Создаем mock DataFrame с заголовками
    df_mock = pd.DataFrame({
        0: ['Компания', 'ИНН', 'Нематериальные активы', 'Выручка'],
        1: ['', '', 'Ф1.1110', 'Ф2.2110']
    })
    start_row = detect_financial_table_start(df_mock)
    assert start_row == 2  # Нематериальные активы на 3-й строке (индекс 2)

def test_extract_years():
    """Тестирует извлечение годов из заголовков"""
    header_row = pd.Series([
        'Показатель', 'Код', 'Ед.изм.', '2,020', '2021', '2022 г.'
    ])
    years = extract_years(header_row)
    assert years == ['2020', '2021', '2022']

def test_load_financial_report(mock_excel_file):
    """Тестирует загрузку финансовой отчетности"""
    df = load_financial_report(mock_excel_file)
    assert not df.empty
    assert '2020' in df.columns
    assert '2021' in df.columns
    assert '2022' in df.columns
    assert len(df) == 3
    assert df[df['Показатель'] == 'Выручка']['2022'].values[0] == 7000000.0