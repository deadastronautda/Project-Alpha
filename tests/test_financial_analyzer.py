import pytest
import pandas as pd
import numpy as np
from app import calculate_ratios, horizontal_analysis, vertical_analysis, get_indicator_value

def test_get_indicator_value(sample_financial_data):
    """Тестирует получение значения показателя"""
    assert get_indicator_value(sample_financial_data, 'Выручка', '2020') == 5000000.0
    assert get_indicator_value(sample_financial_data, 'Чистая прибыль', '2021') == 1500000.0
    assert get_indicator_value(sample_financial_data, 'Себестоимость', '2022') == 5000000.0

def test_calculate_ratios(sample_financial_data):
    """Тестирует расчет финансовых коэффициентов"""
    ratios = calculate_ratios(sample_financial_data)
    
    # Проверяем, что DataFrame не пустой
    assert not ratios.empty
    
    # Проверяем основные коэффициенты
    years = ['2020', '2021', '2022']
    for year in years:
        roe = ratios.loc[ratios['Год'] == year, 'ROE'].values[0]
        expected_roe = 1000000 / 5000000 if year == '2020' else (1500000 / 5000000 if year == '2021' else 2000000 / 5000000)
        assert abs(roe - expected_roe) < 0.001

def test_horizontal_analysis(sample_financial_data):
    """Тестирует горизонтальный анализ"""
    hor_df = horizontal_analysis(sample_financial_data)
    
    # Проверяем, что добавлены столбцы с изменениями
    assert 'Δ 2020→2021, %' in hor_df.columns
    assert 'Δ 2021→2022, %' in hor_df.columns
    
    # Проверяем расчет для выручки
    revenue_row = hor_df[hor_df['Показатель'] == 'Выручка']
    change_2020_2021 = revenue_row['Δ 2020→2021, %'].values[0]
    expected_change = (6000000 - 5000000) / 5000000 * 100
    assert abs(change_2020_2021 - expected_change) < 0.1

def test_vertical_analysis(sample_financial_data):
    """Тестирует вертикальный анализ"""
    vert_df = vertical_analysis(sample_financial_data)
    
    # Проверяем, что есть столбцы с процентами
    assert '2020' in vert_df.columns
    assert '2021' in vert_df.columns
    
    # Для выручки в 2020 году должна быть 100%
    revenue_row = vert_df[vert_df['Показатель'] == 'Выручка']
    assert revenue_row['2020'].values[0] == 100.0