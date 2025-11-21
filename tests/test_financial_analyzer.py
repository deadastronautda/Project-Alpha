import pytest
import pandas as pd
import numpy as np
from app import calculate_financial_ratios, get_indicator_value

def test_get_indicator_value(sample_financial_data):
    """Тестирует получение значения показателя"""
    assert get_indicator_value(sample_financial_data, 'Выручка', '2020') == 5000000.0
    assert get_indicator_value(sample_financial_data, 'Чистая прибыль', '2021') == 1500000.0
    assert get_indicator_value(sample_financial_data, 'Себестоимость', '2022') == 5000000.0

def test_calculate_financial_ratios(sample_financial_data):
    """Тестирует расчет финансовых коэффициентов"""
    ratios = calculate_financial_ratios(sample_financial_data)
    
    # Проверяем, что DataFrame не пустой
    assert not ratios.empty
    
    # Проверяем наличие основных коэффициентов
    expected_columns = ['Год', 'Текущая ликвидность', 'Быстрая ликвидность', 'Абсолютная ликвидность', 'ROA', 'ROE', 'Маржа чистой прибыли', 'Коэффициент автономии']
    assert all(col in ratios.columns for col in expected_columns)
    
    # Проверяем расчет ROE для 2022 года
    roe_2022 = ratios[ratios['Год'] == '2022']['ROE'].values[0]
    expected_roe = 2000000 / (5000000 + 6000000 + 7000000)  # Упрощенный расчет
    assert abs(roe_2022 - expected_roe) < 0.001