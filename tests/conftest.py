import pytest
import pandas as pd
import numpy as np
from io import BytesIO

@pytest.fixture
def sample_financial_data():
    """Создает тестовые финансовые данные"""
    data = {
        'Показатель': ['Выручка', 'Себестоимость продаж', 'Чистая прибыль (убыток)'],
        'Код': ['Ф2.2110', 'Ф2.2120', 'Ф2.2400'],
        'Ед.изм.': ['тыс. руб.', 'тыс. руб.', 'тыс. руб.'],
        '2020': [5000000, 4000000, 1000000],
        '2021': [6000000, 4500000, 1500000],
        '2022': [7000000, 5000000, 2000000]
    }
    return pd.DataFrame(data)

@pytest.fixture
def mock_excel_file():
    """Создает mock Excel файл для тестов"""
    from openpyxl import Workbook
    
    wb = Workbook()
    ws = wb.active
    
    # Создаем тестовые данные в формате отчетности
    test_data = [
        ['Показатель', 'Код', 'Ед.изм.', '2020', '2021', '2022'],
        ['Выручка', 'Ф2.2110', 'тыс. руб.', '5000000', '6000000', '7000000'],
        ['Себестоимость продаж', 'Ф2.2120', 'тыс. руб.', '4000000', '4500000', '5000000'],
        ['Чистая прибыль (убыток)', 'Ф2.2400', 'тыс. руб.', '1000000', '1500000', '2000000']
    ]
    
    for row in test_data:
        ws.append(row)
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer