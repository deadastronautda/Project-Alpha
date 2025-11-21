# financial_analyzer.py
import pandas as pd
import numpy as np
import re
from io import BytesIO

def clean_value(val):
    """Очистка и преобразование числовых значений"""
    if pd.isna(val) or val == '' or val == '-' or str(val).lower() == 'nan' or str(val).lower() == 'н/д':
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

def get_possible_causes(indicator, value, mean_value):
    """Генерация возможных причин для статистических аномалий"""
    if indicator == 'Выручка':
        if value > mean_value:
            return ['Рост рынка', 'Успешное освоение новых сегментов', 'Изменение ценовой политики']
        else:
            return ['Снижение спроса', 'Потеря ключевых клиентов', 'Конкурентное давление']
    
    if indicator == 'Чистая прибыль':
        if value < mean_value:
            return ['Рост издержек', 'Снижение рентабельности', 'Разовые убытки']
        else:
            return ['Оптимизация расходов', 'Рост рентабельности', 'Разовые доходы']
    
    if indicator == 'Дебиторская задолженность':
        if value > mean_value:
            return ['Смягчение кредитной политики', 'Рост продаж в кредит', 'Проблемы с взысканием долгов']
        else:
            return ['Ужесточение кредитной политики', 'Улучшение управления дебиторкой', 'Снижение продаж']
    
    return ['Требуется детальный анализ']

def get_recommendations(indicator, value, mean_value):
    """Рекомендации для статистических аномалий"""
    if indicator == 'Выручка':
        return ['Сравнить динамику с отраслевыми показателями', 'Проанализировать факторы роста/снижения', 'Оценить устойчивость изменений']
    
    if indicator == 'Чистая прибыль':
        return ['Провести факторный анализ прибыли', 'Оценить влияние разовых операций', 'Сравнить с плановыми показателями']
    
    if indicator == 'Дебиторская задолженность':
        return ['Анализ структуры дебиторки по срокам', 'Оценка качества кредитного портфеля', 'Проверка резервов по сомнительным долгам']
    
    return ['Требуется углубленный финансовый анализ']

def get_indicator_value(df, pattern, year=None):
    """Получение значения показателя по шаблону"""
    if df is None:
        return 0.0
    
    df = df.copy()
    df['Показатель'] = df['Показатель'].str.strip().str.lower()
    
    pattern_lower = pattern.lower()
    
    # Ищем точное совпадение сначала
    exact_matches = df[df['Показатель'] == pattern_lower]
    if not exact_matches.empty:
        if year:
            if year in exact_matches.columns:
                return exact_matches.iloc[0][year]
        else:
            # Если год не указан, возвращаем последний доступный год
            year_cols = [col for col in exact_matches.columns if col.isdigit()]
            if year_cols:
                last_year = sorted(year_cols)[-1]
                return exact_matches.iloc[0][last_year]
    
    # Если точного совпадения нет, ищем частичное совпадение
    partial_matches = df[df['Показатель'].str.contains(pattern_lower, na=False)]
    if not partial_matches.empty:
        if year:
            if year in partial_matches.columns:
                return partial_matches.iloc[0][year]
        else:
            year_cols = [col for col in partial_matches.columns if col.isdigit()]
            if year_cols:
                last_year = sorted(year_cols)[-1]
                return partial_matches.iloc[0][last_year]
    
    return 0.0

def detect_anomalies(df):
    """Обнаружение аномалий в финансовых данных"""
    if df is None:
        return []
    
    anomalies = []
    years = [col for col in df.columns if col.isdigit()]
    
    try:
        # Проверяем статистические аномалии
        key_indicators = ['Выручка', 'Чистая прибыль', 'Дебиторская задолженность']
        for indicator in key_indicators:
            values = [get_indicator_value(df, indicator, year) for year in years]
            if len(values) >= 3:  # Нужно минимум 3 года для анализа
                # Рассчитываем среднее и стандартное отклонение
                mean_value = np.mean(values)
                std_value = np.std(values)
                
                if std_value > 0:  # Избегаем деления на ноль
                    for i, year in enumerate(years):
                        z_score = (values[i] - mean_value) / std_value
                        if abs(z_score) > 3:  # Порог в 3 стандартных отклонения
                            anomalies.append({
                                'indicator': indicator,
                                'year': year,
                                'value': values[i],
                                'mean_value': mean_value,
                                'deviation': ((values[i] - mean_value) / mean_value * 100) if mean_value != 0 else 0,
                                'type': 'Статистическая',
                                'severity': 'high' if abs(z_score) > 4 else 'medium',
                                'z_score': z_score
                            })
        
        # Проверяем бизнес-логические аномалии
        for i in range(1, len(years)):
            prev_year = years[i-1]
            curr_year = years[i]
            
            # Отрицательная прибыль при росте выручки
            profit_prev = get_indicator_value(df, 'Чистая прибыль', prev_year)
            profit_curr = get_indicator_value(df, 'Чистая прибыль', curr_year)
            revenue_prev = get_indicator_value(df, 'Выручка', prev_year)
            revenue_curr = get_indicator_value(df, 'Выручка', curr_year)
            
            if profit_curr < 0 and profit_prev >= 0 and revenue_curr > revenue_prev:
                revenue_growth = ((revenue_curr - revenue_prev) / revenue_prev * 100) if revenue_prev != 0 else 0
                anomalies.append({
                    'indicator': 'Чистая прибыль',
                    'year': curr_year,
                    'value': profit_curr,
                    'type': 'Бизнес-логика',
                    'severity': 'high'
                })
        
        return anomalies
    except Exception as e:
        print(f"Ошибка при обнаружении аномалий: {str(e)}")
        return []

def load_financial_report(file_path):
    """Загрузка финансовой отчетности"""
    try:
        # Читаем Excel файл
        df = pd.read_excel(file_path, header=None)
        
        # Находим начало финансовой отчетности
        start_row = detect_financial_table_start(df)
        report_part = df.iloc[start_row:].reset_index(drop=True)
        
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