import pytest
import pandas as pd
import numpy as np
from app import detect_anomalies, get_possible_causes, get_recommendations

def test_detect_anomalies_no_anomalies(sample_financial_data):
    """Тестирует обнаружение аномалий при нормальных данных"""
    anomalies = detect_anomalies(sample_financial_data)
    assert isinstance(anomalies, list)
    assert len(anomalies) == 0  # В тестовых данных нет аномалий

def test_get_possible_causes():
    """Тестирует получение возможных причин"""
    causes = get_possible_causes('Выручка', 1000000, 500000)
    assert isinstance(causes, list)
    assert len(causes) > 0

def test_get_recommendations():
    """Тестирует получение рекомендаций"""
    recommendations = get_recommendations('Чистая прибыль', 500000, 1000000)
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0