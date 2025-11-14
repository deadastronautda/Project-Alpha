import pytest
import pandas as pd
from app import load_financial_report, clean_value, detect_financial_table_start, extract_years

def test_clean_value():
    """Тестирует очистку числовых значений"""
    assert clean_value("1,146") == 1.146
    assert clean_value("662,006") == 662.006
    assert clean_value("") is None
    assert clean_value("0") == 0.0
    assert clean_value("-373840") == -373.840
    assert clean_value("н/д") is None

def test_detect_financial_table_start(sample_financial_data):
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
        'Показатель', 'Код', 'Ед.изм.', '2,010', '2011', '2012', '2013'
    ])
    years = extract_years(header_row)
    assert years == ['2010', '2011', '2012', '2013']

def test_load_financial_report(mock_excel_file):
    """Тестирует загрузку финансовой отчетности"""
    df = load_financial_report(mock_excel_file)
    assert not df.empty
    assert '2020' in df.columns
    assert '2021' in df.columns
    assert '2022' in df.columns
    assert len(df) == 3  # 3 показателя
    assert df[df['Показатель'] == 'Выручка']['2022'].values[0] == 7000000.0