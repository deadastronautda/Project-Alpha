import pytest
import pandas as pd
import numpy as np
from app import detect_anomalies, get_possible_causes, get_recommendations

def test_detect_anomalies_no_anomalies(sample_financial_data):
    """Тестирует обнаружение аномалий при нормальных данных"""
    # Добавляем баланс для валидации
    balance_data = pd.DataFrame({
        'Показатель': ['БАЛАНС (актив)', 'БАЛАНС (пассив)'],
        'Код': ['Ф1.1600', 'Ф1.1700'],
        'Ед.изм.': ['тыс. руб.', 'тыс. руб.'],
        '2020': [8000000, 8000000],
        '2021': [9000000, 9000000],
        '2022': [10000000, 10000000]
    })
    full_data = pd.concat([sample_financial_data, balance_data], ignore_index=True)
    
    ratios = calculate_financial_ratios(full_data)
    anomalies = detect_anomalies(full_data, ratios)
    assert len(anomalies) == 0

def test_detect_anomalies_statistical_anomaly():
    """Тестирует обнаружение статистической аномалии"""
    # Создаем данные с аномальным значением
    data = {
        'Показатель': ['Выручка'] * 5,
        'Код': ['Ф2.2110'] * 5,
        'Ед.изм.': ['тыс. руб.'] * 5,
        '2018': [5000000],
        '2019': [5200000],
        '2020': [5100000],
        '2021': [5300000],
        '2022': [15000000]  # Аномальное значение
    }
    df = pd.DataFrame(data)
    
    # Добавляем баланс
    balance_data = pd.DataFrame({
        'Показатель': ['БАЛАНС (актив)', 'БАЛАНС (пассив)'],
        'Код': ['Ф1.1600', 'Ф1.1700'],
        'Ед.изм.': ['тыс. руб.', 'тыс. руб.'],
        '2018': [10000000, 10000000],
        '2019': [10000000, 10000000],
        '2020': [10000000, 10000000],
        '2021': [10000000, 10000000],
        '2022': [20000000, 20000000]
    })
    full_data = pd.concat([df, balance_data], ignore_index=True)
    
    ratios = calculate_financial_ratios(full_data)
    anomalies = detect_anomalies(full_data, ratios)
    assert len(anomalies) > 0
    assert any('статистическая' in a['type'].lower() for a in anomalies)

def test_get_possible_causes():
    """Тестирует генерацию возможных причин"""
    causes = get_possible_causes('Выручка', 10000000, 5000000)
    assert len(causes) > 0
    assert any('рост' in cause.lower() for cause in causes)

def test_get_recommendations():
    """Тестирует генерацию рекомендаций"""
    recommendations = get_recommendations('Чистая прибыль', 1000000, 2000000)
    assert len(recommendations) > 0
    assert any('анализ' in rec.lower() for rec in recommendations)