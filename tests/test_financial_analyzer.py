import pytest
import pandas as pd
import numpy as np
from app import get_indicator_value

def test_get_indicator_value(sample_financial_data):
    """Тестирует получение значения показателя"""
    assert get_indicator_value(sample_financial_data, 'Выручка', '2020') == 5000000.0
    assert get_indicator_value(sample_financial_data, 'Чистая прибыль', '2021') == 1500000.0
    assert get_indicator_value(sample_financial_data, 'Себестоимость', '2022') == 5000000.0