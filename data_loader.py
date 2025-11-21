import pandas as pd
import re
from io import BytesIO

def clean_value(val):
    """Очистка и преобразование числовых значений"""
    if pd.isna(val) or val == '' or val == '-' or str(val).lower() == 'nan':
        return None
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        # Удаляем пробелы и заменяем запятые на точки
        val = re.sub(r'[^\d\.,\-]', '', val)
        val = val.replace(',', '.')
        try:
            return float(val)
        except ValueError:
            return None
    return None

def detect_financial_table_start(df):
    """Определение начала финансовой отчетности"""
    for idx, row in df.iterrows():
        if any(keyword in str(row.iloc[0]).lower() for keyword in ['нематериальные активы', 'нематериальные', 'активы', 'пассивы']):
            return idx
    return 26  # Стандартное значение, если не найдено

def extract_years(header_row):
    """Извлечение годов из заголовков"""
    years = []
    for cell in header_row.iloc[3:]:
        cell_str = str(cell).strip()
        # Ищем годы в форматах: 2020, 2,020, 2020 г., 2020 год
        match = re.search(r'(?:2,?0[0-9]{2}|[1-2][0-9]{3})', cell_str)
        if match:
            year_str = match.group(0).replace(',', '')
            try:
                year = int(year_str)
                if 1990 <= year <= 2100:  # Проверяем диапазон
                    years.append(str(year))
            except ValueError:
                continue
    return years

def load_financial_report(uploaded_file):
    """Загрузка и обработка финансовой отчетности"""
    try:
        # Читаем Excel файл
        df_raw = pd.read_excel(uploaded_file, header=None, dtype=str)
        
        # Находим начало финансовой отчетности
        start_row = detect_financial_table_start(df_raw)
        report_part = df_raw.iloc[start_row:].reset_index(drop=True)
        
        # Извлекаем годы
        years = extract_years(report_part.iloc[0])
        if not years:
            raise ValueError("Не удалось определить годы в отчете")
        
        # Создаем столбцы
        column_names = ['Показатель', 'Код', 'Ед.изм.'] + years
        data_rows = report_part.iloc[1:, :len(column_names)].copy()
        data_rows.columns = column_names
        
        # Преобразуем числовые значения
        for year in years:
            if year in data_rows.columns:
                data_rows[year] = data_rows[year].apply(clean_value)
        
        # Удаляем пустые строки
        data_rows = data_rows.dropna(subset=['Показатель'], how='all')
        data_rows['Показатель'] = data_rows['Показатель'].str.strip()
        
        return data_rows.reset_index(drop=True)
    
    except Exception as e:
        print(f"Ошибка при загрузке файла: {str(e)}")
        return None