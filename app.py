import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re
from io import BytesIO

# Настройка страницы
st.set_page_config(
    page_title="Финансовый анализатор ООО 'Агрисовгаз'",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кэширование загрузки данных
@st.cache_data
def load_data(file):
    """Загружает данные из Excel файла"""
    try:
        df = pd.read_excel(file)
        return df
    except Exception as e:
        st.error(f"Ошибка при загрузке файла: {e}")
        return None

def preprocess_data(df):
    """Предобрабатывает данные для анализа"""
    # Очистка данных
    df['Значение'] = pd.to_numeric(df['Значение'], errors='coerce')
    
    # Проверка на пустые значения
    if df['Значение'].isnull().any():
        st.warning("В данных обнаружены пустые значения. Они будут заменены на 0.")
        df['Значение'] = df['Значение'].fillna(0)
    
    return df

def calculate_financial_ratios(df):
    """Рассчитывает финансовые коэффициенты"""
    # Получаем последний год для расчета
    recent_year = df['Год'].max()
    
    # Фильтруем данные за последний год
    recent_data = df[df['Год'] == recent_year].set_index('Показатель')['Значение']
    
    # Проверяем наличие необходимых данных
    required_indicators = {
        'Текущая ликвидность': ['Итого по разделу II - Оборотные активы', 'Итого по разделу V - Краткосрочные обязательства'],
        'Быстрая ликвидность': ['Итого по разделу II - Оборотные активы', 'Запасы', 'Итого по разделу V - Краткосрочные обязательства'],
        'Абсолютная ликвидность': ['Денежные средства и денежные эквиваленты', 'Итого по разделу V - Краткосрочные обязательства'],
        'ROA': ['Чистая прибыль (убыток)', 'БАЛАНС (актив)'],
        'ROE': ['Чистая прибыль (убыток)', 'Итого по разделу III - Капитал и резервы'],
        'Маржа чистой прибыли': ['Чистая прибыль (убыток)', 'Выручка'],
        'Коэффициент автономии': ['Итого по разделу III - Капитал и резервы', 'БАЛАНС (актив)'],
    }
    
    ratios = {}
    missing_indicators = []
    
    for ratio_name, indicators in required_indicators.items():
        try:
            if ratio_name == 'Текущая ликвидность':
                current_assets = recent_data.get('Итого по разделу II - Оборотные активы', 0)
                short_liabilities = recent_data.get('Итого по разделу V - Краткосрочные обязательства', 1)
                value = current_assets / short_liabilities if short_liabilities != 0 else np.nan
                
            elif ratio_name == 'Быстрая ликвидность':
                current_assets = recent_data.get('Итого по разделу II - Оборотные активы', 0)
                inventory = recent_data.get('Запасы', 0)
                short_liabilities = recent_data.get('Итого по разделу V - Краткосрочные обязательства', 1)
                value = (current_assets - inventory) / short_liabilities if short_liabilities != 0 else np.nan
                
            elif ratio_name == 'Абсолютная ликвидность':
                cash = recent_data.get('Денежные средства и денежные эквиваленты', 0)
                short_liabilities = recent_data.get('Итого по разделу V - Краткосрочные обязательства', 1)
                value = cash / short_liabilities if short_liabilities != 0 else np.nan
                
            elif ratio_name == 'ROA':
                net_profit = recent_data.get('Чистая прибыль (убыток)', 0)
                total_assets = recent_data.get('БАЛАНС (актив)', 1)
                value = net_profit / total_assets if total_assets != 0 else np.nan
                
            elif ratio_name == 'ROE':
                net_profit = recent_data.get('Чистая прибыль (убыток)', 0)
                equity = recent_data.get('Итого по разделу III - Капитал и резервы', 1)
                value = net_profit / equity if equity != 0 else np.nan
                
            elif ratio_name == 'Маржа чистой прибыли':
                net_profit = recent_data.get('Чистая прибыль (убыток)', 0)
                revenue = recent_data.get('Выручка', 1)
                value = net_profit / revenue if revenue != 0 else np.nan
                
            elif ratio_name == 'Коэффициент автономии':
                equity = recent_data.get('Итого по разделу III - Капитал и резервы', 0)
                total_assets = recent_data.get('БАЛАНС (актив)', 1)
                value = equity / total_assets if total_assets != 0 else np.nan
                
            ratios[ratio_name] = {
                'value': value,
                'norm': get_norm_value(ratio_name),
                'interpretation': interpret_ratio(ratio_name, value)
            }
        except KeyError as e:
            missing_indicators.append(str(e))
    
    if missing_indicators:
        st.warning(f"Не хватает данных для расчета некоторых коэффициентов: {', '.join(missing_indicators)}")
    
    return ratios

def get_norm_value(ratio_name):
    """Возвращает нормативное значение для коэффициента"""
    norms = {
        'Текущая ликвидность': 2.0,
        'Быстрая ликвидность': 1.0,
        'Абсолютная ликвидность': 0.2,
        'ROA': 0.05,
        'ROE': 0.15,
        'Маржа чистой прибыли': 0.1,
        'Коэффициент автономии': 0.5,
    }
    return norms.get(ratio_name, 0)

def interpret_ratio(ratio_name, value):
    """Интерпретирует значение коэффициента"""
    if pd.isna(value) or value is None:
        return "Недостаточно данных для интерпретации"
    
    if ratio_name in ['Текущая ликвидность', 'Быстрая ликвидность', 'Абсолютная ликвидность', 'ROA', 'ROE', 'Маржа чистой прибыли', 'Коэффициент автономии']:
        if value >= get_norm_value(ratio_name):
            return "✅ Хорошее значение"
        elif value >= get_norm_value(ratio_name) * 0.7:
            return "🟡 Удовлетворительное значение"
        else:
            return "❌ Низкое значение"
    
    return ""

def perform_horizontal_analysis(df):
    """Выполняет горизонтальный анализ (динамика)"""
    # Получаем показатели для анализа
    key_indicators = [
        'Выручка',
        'Себестоимость продаж', 
        'Чистая прибыль (убыток)',
        'БАЛАНС (актив)',
        'Итого по разделу III - Капитал и резервы',
        'Итого по разделу V - Краткосрочные обязательства'
    ]
    
    # Фильтруем интересующие нас показатели
    filtered_df = df[df['Показатель'].isin(key_indicators)]
    
    # Создаем сводную таблицу с годами в столбцах
    pivot_df = filtered_df.pivot_table(
        index='Показатель', 
        columns='Год', 
        values='Значение', 
        aggfunc='sum'
    ).reset_index()
    
    # Рассчитываем абсолютные и относительные изменения
    years = sorted(pivot_df.columns[1:])
    for i in range(1, len(years)):
        prev_year = years[i-1]
        curr_year = years[i]
        
        # Абсолютное изменение
        pivot_df[f'Δ {prev_year}-{curr_year}'] = pivot_df[curr_year] - pivot_df[prev_year]
        
        # Относительное изменение в процентах
        pivot_df[f'Δ% {prev_year}-{curr_year}'] = np.where(
            pivot_df[prev_year] != 0,
            (pivot_df[curr_year] - pivot_df[prev_year]) / abs(pivot_df[prev_year]) * 100,
            np.nan
        )
    
    return pivot_df

def perform_vertical_analysis(df, year=None):
    """Выполняет вертикальный анализ (структура)"""
    if year is None:
        year = df['Год'].max()
    
    # Фильтруем данные за указанный год
    year_df = df[df['Год'] == year].copy()
    
    # Структура актива баланса
    asset_items = [
        'Нематериальные активы',
        'Основные средства',
        'Запасы',
        'Дебиторская задолженность',
        'Денежные средства и денежные эквиваленты',
        'Прочие внеоборотные активы',
        'Прочие оборотные активы'
    ]
    
    # Структура пассива баланса
    liability_items = [
        'Уставный капитал (складочный капитал, уставный фонд, вклады товарищей)',
        'Нераспределенная прибыль (непокрытый убыток)',
        'Заемные средства',
        'Кредиторская задолженность',
        'Отложенные налоговые обязательства'
    ]
    
    # Фильтруем структурные показатели
    asset_df = year_df[year_df['Показатель'].isin(asset_items)].copy()
    liability_df = year_df[year_df['Показатель'].isin(liability_items)].copy()
    
    # Получаем итоговые значения для расчета долей
    total_assets = year_df[year_df['Показатель'] == 'БАЛАНС (актив)']['Значение'].values[0] if not year_df[year_df['Показатель'] == 'БАЛАНС (актив)'].empty else 1
    total_liabilities = year_df[year_df['Показатель'] == 'БАЛАНС (пассив)']['Значение'].values[0] if not year_df[year_df['Показатель'] == 'БАЛАНС (пассив)'].empty else 1
    
    # Рассчитываем доли в процентах
    asset_df['Доля, %'] = asset_df['Значение'] / total_assets * 100
    liability_df['Доля, %'] = liability_df['Значение'] / total_liabilities * 100
    
    return asset_df, liability_df

def detect_anomalies(df):
    """Обнаруживает аномалии в финансовых данных"""
    anomalies = []
    
    # 1. Проверка на резкие изменения в динамике (Z-score)
    key_indicators = [
        'Выручка',
        'Чистая прибыль (убыток)',
        'Дебиторская задолженность',
        'Кредиторская задолженность'
    ]
    
    # Для каждого показателя рассчитываем Z-score
    for indicator in key_indicators:
        indicator_data = df[df['Показатель'] == indicator]
        if not indicator_data.empty:
            for year in sorted(indicator_data['Год'].unique()):
                year_value = indicator_data[indicator_data['Год'] == year]['Значение'].values[0]
                
                # Рассчитываем Z-score
                mean_value = indicator_data['Значение'].mean()
                std_value = indicator_data['Значение'].std()
                
                if std_value > 0:  # Избегаем деления на ноль
                    z_score = (year_value - mean_value) / std_value
                    
                    # Если Z-score больше 3 или меньше -3, считаем это аномалией
                    if abs(z_score) > 3:
                        anomalies.append({
                            'type': 'Статистическая',
                            'indicator': indicator,
                            'year': year,
                            'value': year_value,
                            'z_score': z_score,
                            'severity': 'high' if abs(z_score) > 4 else 'medium',
                            'description': f"Резкое {'увеличение' if z_score > 0 else 'снижение'} показателя ({z_score:.2f} стандартных отклонений от среднего)"
                        })
    
    # 2. Проверка на бизнес-логические аномалии
    
    # 2.1. Отрицательная прибыль при росте выручки
    profit_data = df[df['Показатель'] == 'Чистая прибыль (убыток)']
    revenue_data = df[df['Показатель'] == 'Выручка']
    
    if not profit_data.empty and not revenue_data.empty:
        years = sorted(profit_data['Год'].unique())
        for i in range(1, len(years)):
            prev_year = years[i-1]
            curr_year = years[i]
            
            prev_profit = profit_data[profit_data['Год'] == prev_year]['Значение'].values[0]
            curr_profit = profit_data[profit_data['Год'] == curr_year]['Значение'].values[0]
            prev_revenue = revenue_data[revenue_data['Год'] == prev_year]['Значение'].values[0]
            curr_revenue = revenue_data[revenue_data['Год'] == curr_year]['Значение'].values[0]
            
            # Проверяем условие аномалии
            if curr_profit < 0 and curr_revenue > prev_revenue:
                anomalies.append({
                    'type': 'Бизнес-логика',
                    'indicator': 'Чистая прибыль',
                    'year': curr_year,
                    'value': curr_profit,
                    'severity': 'high',
                    'description': f"Отрицательная чистая прибыль при росте выручки с {prev_year} по {curr_year} год"
                })
    
    # 2.2. Рост дебиторской задолженности быстрее выручки
    receivables_data = df[df['Показатель'] == 'Дебиторская задолженность']
    
    if not receivables_data.empty and not revenue_data.empty:
        years = sorted(receivables_data['Год'].unique())
        for i in range(1, len(years)):
            prev_year = years[i-1]
            curr_year = years[i]
            
            prev_receivables = receivables_data[receivables_data['Год'] == prev_year]['Значение'].values[0]
            curr_receivables = receivables_data[receivables_data['Год'] == curr_year]['Значение'].values[0]
            prev_revenue = revenue_data[revenue_data['Год'] == prev_year]['Значение'].values[0]
            curr_revenue = revenue_data[revenue_data['Год'] == curr_year]['Значение'].values[0]
            
            # Рассчитываем темпы роста
            receivables_growth = (curr_receivables - prev_receivables) / prev_receivables if prev_receivables != 0 else 0
            revenue_growth = (curr_revenue - prev_revenue) / prev_revenue if prev_revenue != 0 else 0
            
            # Проверяем условие аномалии
            if receivables_growth > revenue_growth * 1.5 and receivables_growth > 0:
                anomalies.append({
                    'type': 'Бизнес-логика',
                    'indicator': 'Дебиторская задолженность',
                    'year': curr_year,
                    'value': curr_receivables,
                    'severity': 'medium',
                    'description': f"Рост дебиторской задолженности ({receivables_growth:.1%}) значительно опережает рост выручки ({revenue_growth:.1%})"
                })
    
    # 2.3. Низкая текущая ликвидность
    short_liabilities = df[df['Показатель'] == 'Итого по разделу V - Краткосрочные обязательства']
    current_assets = df[df['Показатель'] == 'Итого по разделу II - Оборотные активы']
    
    if not short_liabilities.empty and not current_assets.empty:
        for year in sorted(short_liabilities['Год'].unique()):
            liabilities = short_liabilities[short_liabilities['Год'] == year]['Значение'].values[0]
            assets = current_assets[current_assets['Год'] == year]['Значение'].values[0]
            
            current_ratio = assets / liabilities if liabilities != 0 else np.inf
            
            # Проверяем условие аномалии
            if current_ratio < 1:
                anomalies.append({
                    'type': 'Бизнес-логика',
                    'indicator': 'Текущая ликвидность',
                    'year': year,
                    'value': current_ratio,
                    'severity': 'high',
                    'description': f"Коэффициент текущей ликвидности ниже критического уровня ({current_ratio:.2f} < 1)"
                })
    
    return anomalies

# Функции визуализации
def plot_key_indicators_trend(df):
    """Строит график динамики ключевых показателей"""
    key_indicators = [
        'Выручка',
        'Чистая прибыль (убыток)',
        'БАЛАНС (актив)',
        'Итого по разделу III - Капитал и резервы'
    ]
    
    filtered_df = df[df['Показатель'].isin(key_indicators)]
    
    fig = px.line(
        filtered_df,
        x='Год',
        y='Значение',
        color='Показатель',
        title='Динамика ключевых финансовых показателей',
        markers=True
    )
    
    fig.update_layout(
        xaxis_title='Год',
        yaxis_title='Значение, тыс. руб.',
        hovermode="x unified",
        legend_title_text='Показатели'
    )
    
    return fig

def plot_financial_ratios(ratios):
    """Строит график финансовых коэффициентов"""
    ratio_names = list(ratios.keys())
    values = [ratios[name]['value'] for name in ratio_names]
    norms = [ratios[name]['norm'] for name in ratio_names]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=ratio_names,
        y=values,
        name='Фактическое значение',
        marker_color='steelblue'
    ))
    
    fig.add_trace(go.Scatter(
        x=ratio_names,
        y=norms,
        mode='lines+markers',
        name='Нормативное значение',
        line=dict(color='red', dash='dash'),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Финансовые коэффициенты с нормативными значениями',
        xaxis_title='Коэффициенты',
        yaxis_title='Значение',
        barmode='group',
        hovermode="x unified"
    )
    
    return fig

def plot_asset_structure(asset_df):
    """Строит график структуры активов"""
    fig = px.pie(
        asset_df,
        names='Показатель',
        values='Значение',
        title='Структура активов',
        hole=0.3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

def plot_anomaly_visualization(df, anomalies):
    """Визуализирует обнаруженные аномалии"""
    if not anomalies:
        return None
    
    # Создаем DataFrame для визуализации
    anomaly_years = [a['year'] for a in anomalies]
    anomaly_indicators = list(set([a['indicator'] for a in anomalies]))
    
    # Фильтруем данные только для аномальных показателей
    anomaly_df = df[df['Показатель'].isin(anomaly_indicators)]
    
    fig = px.line(
        anomaly_df,
        x='Год',
        y='Значение',
        color='Показатель',
        title='Динамика показателей с обнаруженными аномалиями',
        markers=True
    )
    
    # Выделяем аномальные точки
    for anomaly in anomalies:
        fig.add_trace(go.Scatter(
            x=[anomaly['year']],
            y=[anomaly['value']],
            mode='markers',
            marker=dict(
                size=15,
                color='red',
                symbol='x',
                line=dict(width=2, color='white')
            ),
            name=f"{anomaly['indicator']} ({anomaly['year']})",
            hovertemplate=f"<b>{anomaly['indicator']}</b><br>Год: {anomaly['year']}<br>Значение: {anomaly['value']:.0f}<br><i>{anomaly['description']}</i><extra></extra>"
        ))
    
    fig.update_layout(
        xaxis_title='Год',
        yaxis_title='Значение',
        hovermode="x unified",
        legend_title_text='Показатели'
    )
    
    return fig

def generate_pdf_report(df, ratios, horizontal_df, vertical_asset_df, vertical_liability_df, anomalies):
    """Генерирует PDF-отчет с результатами анализа"""
    from fpdf import FPDF
    
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'Финансовый анализ ООО "Агрисовгаз"', 0, 1, 'C')
            self.ln(5)
        
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Страница {self.page_no()}', 0, 0, 'C')
        
        def chapter_title(self, title):
            self.set_font('Arial', 'B', 14)
            self.cell(0, 10, title, 0, 1, 'L')
            self.ln(4)
        
        def chapter_body(self, body):
            self.set_font('Arial', '', 12)
            self.multi_cell(0, 6, body)
            self.ln()
        
        def add_table(self, header, data):
            self.set_font('Arial', 'B', 10)
            col_width = self.w / (len(header) + 1)
            
            # Заголовки
            for item in header:
                self.cell(col_width, 10, str(item), border=1)
            self.ln()
            
            # Данные
            self.set_font('Arial', '', 10)
            for row in data:
                for item in row:
                    self.cell(col_width, 8, str(item), border=1)
                self.ln()
    
    pdf = PDF()
    pdf.add_page()
    
    # Введение
    pdf.chapter_title('1. Введение')
    intro_text = f"""
    Настоящий отчет подготовлен на основе финансовой отчетности ООО "Агрисовгаз" за период с {df['Год'].min()} по {df['Год'].max()} год.
    Цель анализа - оценка финансового состояния компании, выявление позитивных и негативных тенденций, а также обнаружение возможных аномалий.
    """
    pdf.chapter_body(intro_text)
    
    # Горизонтальный анализ
    pdf.chapter_title('2. Горизонтальный анализ')
    horiz_text = """
    Горизонтальный анализ позволяет оценить динамику изменения финансовых показателей в течение анализируемого периода.
    """
    pdf.chapter_body(horiz_text)
    
    # Финансовые коэффициенты
    pdf.chapter_title('3. Финансовые коэффициенты')
    ratios_text = "В таблице представлены ключевые финансовые коэффициенты за последний год:\n"
    pdf.chapter_body(ratios_text)
    
    ratio_data = []
    for ratio_name, data in ratios.items():
        ratio_data.append([
            ratio_name,
            f"{data['value']:.3f}" if not pd.isna(data['value']) else "Н/Д",
            f"{data['norm']:.3f}",
            data['interpretation']
        ])
    
    pdf.add_table(['Коэффициент', 'Значение', 'Норматив', 'Интерпретация'], ratio_data)
    
    # Аномалии
    pdf.chapter_title('4. Выявленные аномалии')
    if anomalies:
        anomaly_text = f"В ходе анализа выявлено {len(anomalies)} аномалий:\n"
        pdf.chapter_body(anomaly_text)
        
        anomaly_data = []
        for anomaly in anomalies:
            anomaly_data.append([
                anomaly['indicator'],
                anomaly['year'],
                f"{anomaly['value']:.0f}",
                anomaly['type'],
                anomaly['severity'].upper(),
                anomaly['description']
            ])
        
        pdf.add_table(['Показатель', 'Год', 'Значение', 'Тип', 'Важность', 'Описание'], anomaly_data)
    else:
        pdf.chapter_body("В ходе анализа не выявлено значимых аномалий.")
    
    # Заключение
    pdf.chapter_title('5. Заключение')
    conclusion_text = """
    По результатам проведенного анализа можно сделать следующие выводы:
    """
    
    # Добавляем выводы на основе анализа коэффициентов
    positive_ratios = sum(1 for r in ratios.values() if 'Хорошее' in r['interpretation'])
    total_ratios = len(ratios)
    
    if positive_ratios / total_ratios > 0.7:
        conclusion_text += "\n- Финансовое состояние компании можно оценить как хорошее."
    elif positive_ratios / total_ratios > 0.4:
        conclusion_text += "\n- Финансовое состояние компании можно оценить как удовлетворительное с отдельными проблемными зонами."
    else:
        conclusion_text += "\n- Финансовое состояние компании вызывает серьезные опасения."
    
    if anomalies:
        high_severity = sum(1 for a in anomalies if a['severity'] == 'high')
        if high_severity > 0:
            conclusion_text += f"\n- Выявлено {high_severity} критически важных аномалий, требующих немедленного внимания."
    
    conclusion_text += "\n\nРекомендуется провести детальный анализ выявленных проблем и разработать план их устранения."
    pdf.chapter_body(conclusion_text)
    
    # Сохраняем PDF в буфер
    pdf_output = BytesIO()
    pdf_content = pdf.output(dest='S').encode('latin1')
    pdf_output.write(pdf_content)
    pdf_output.seek(0)
    
    return pdf_output

# Заголовок приложения
st.title("📊 Финансовый анализатор ООО 'Агрисовгаз'")
st.markdown("""
    Это приложение выполняет комплексный анализ финансовой отчетности в формате Excel.
    Загрузите файл финансовой отчетности, и приложение автоматически:
    - Проведет горизонтальный и вертикальный анализ
    - Рассчитает ключевые финансовые коэффициенты
    - Выявит возможные аномалии в данных
    - Предоставит наглядную визуализацию результатов
""")

# Боковая панель
with st.sidebar:
    st.header("📁 Загрузка данных")
    uploaded_file = st.file_uploader(
        "Выберите Excel-файл с финансовой отчетностью", 
        type=["xlsx", "xls"],
        accept_multiple_files=False
    )
    
    st.markdown("---")
    st.header("⚙️ Настройки анализа")
    
    # Год для вертикального анализа
    selected_year = None
    if uploaded_file is not None:
        df_temp = load_data(uploaded_file)
        if df_temp is not None:
            available_years = sorted(df_temp['Год'].unique())
            selected_year = st.selectbox("Выберите год для вертикального анализа", available_years, index=len(available_years)-1)
    
    st.markdown("---")
    st.header("💡 О приложении")
    st.markdown("""
    **Версия:** 1.0  
    **Источник данных:** [list-org.com](https://www.list-org.com)  
    **Разработчик:** Финансовый аналитик
    """)

# Основной контент
if uploaded_file is None:
    st.info("👈 Пожалуйста, загрузите Excel-файл финансовой отчетности в боковой панели для начала анализа.")
    
    # Показываем пример данных
    st.subheader("Пример формата данных:")
    sample_data = {
        'Показатель': ['Выручка', 'Себестоимость продаж', 'Чистая прибыль (убыток)'],
        'Код': ['Ф2.2110', 'Ф2.2120', 'Ф2.2400'],
        'Ед.изм.': ['тыс. руб.', 'тыс. руб.', 'тыс. руб.'],
        'Год': [2022, 2022, 2022],
        'Значение': [10883500, 9589230, 116913]
    }
    sample_df = pd.DataFrame(sample_data)
    st.dataframe(sample_df, hide_index=True)

else:
    # Загружаем и предобрабатываем данные
    with st.spinner('Загрузка и обработка данных...'):
        df = load_data(uploaded_file)
    
    if df is not None:
        df = preprocess_data(df)
        
        st.success("✅ Данные успешно загружены и обработаны!")
        st.caption(f"Загружено записей: {len(df)} за период с {df['Год'].min()} по {df['Год'].max()} год")
        
        # Выполняем расчеты
        with st.spinner('Выполнение финансового анализа...'):
            # Финансовые коэффициенты
            ratios = calculate_financial_ratios(df)
            
            # Горизонтальный анализ
            horizontal_df = perform_horizontal_analysis(df)
            
            # Вертикальный анализ
            vertical_asset_df, vertical_liability_df = perform_vertical_analysis(df, selected_year)
            
            # Обнаружение аномалий
            anomalies = detect_anomalies(df)
        
        # Создаем вкладки
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Обзор", 
            "📊 Горизонтальный анализ", 
            "📉 Вертикальный анализ", 
            "🔍 Аномалии", 
            "💡 Коэффициенты"
        ])
        
        with tab1:
            st.header("📈 Обзор финансовых показателей")
            
            # График динамики ключевых показателей
            fig_trend = plot_key_indicators_trend(df)
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Сводная таблица по последнему году
            st.subheader("Основные показатели за последний год")
            last_year = df['Год'].max()
            last_year_df = df[df['Год'] == last_year]
            key_indicators = [
                'Выручка',
                'Себестоимость продаж',
                'Валовая прибыль (убыток)',
                'Чистая прибыль (убыток)',
                'БАЛАНС (актив)',
                'Итого по разделу III - Капитал и резервы'
            ]
            
            summary_df = last_year_df[last_year_df['Показатель'].isin(key_indicators)]
            if not summary_df.empty:
                st.dataframe(
                    summary_df[['Показатель', 'Значение']].style.format({
                        'Значение': '{:,.0f}'.format
                    }),
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.warning("Нет данных для отображения основных показателей за последний год.")
        
        with tab2:
            st.header("📊 Горизонтальный анализ (динамика)")
            st.markdown("""
            Горизонтальный анализ позволяет оценить изменение финансовых показателей во времени.
            В таблице представлены как абсолютные, так и относительные изменения ключевых показателей.
            """)
            
            # Показываем таблицу с горизонтальным анализом
            st.dataframe(
    horizontal_df.style.format({
        **{year: '{:,.0f}'.format for year in horizontal_df.columns if isinstance(year, int)},
        **{col: '{:+,.0f}'.format for col in horizontal_df.columns if isinstance(col, str) and 'Δ ' in col},
        **{col: '{:+,.1f}%'.format for col in horizontal_df.columns if isinstance(col, str) and 'Δ%' in col}
    }),
    use_container_width=True,
    hide_index=True
)
        
        with tab3:
            st.header(f"📉 Вертикальный анализ (структура за {selected_year} год)")
            st.markdown("""
            Вертикальный анализ показывает структуру финансовых показателей в процентах от итоговых значений.
            Это позволяет оценить долю каждого элемента в общей структуре активов или обязательств.
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Структура активов")
                if not vertical_asset_df.empty:
                    st.dataframe(
                        vertical_asset_df[['Показатель', 'Значение', 'Доля, %']].style.format({
                            'Значение': '{:,.0f}'.format,
                            'Доля, %': '{:.1f}%'.format
                        }),
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    fig_asset = plot_asset_structure(vertical_asset_df)
                    st.plotly_chart(fig_asset, use_container_width=True)
                else:
                    st.warning("Нет данных для анализа структуры активов за выбранный год.")
            
            with col2:
                st.subheader("Структура обязательств и капитала")
                if not vertical_liability_df.empty:
                    st.dataframe(
                        vertical_liability_df[['Показатель', 'Значение', 'Доля, %']].style.format({
                            'Значение': '{:,.0f}'.format,
                            'Доля, %': '{:.1f}%'.format
                        }),
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.warning("Нет данных для анализа структуры обязательств за выбранный год.")
        
        with tab4:
            st.header("🔍 Обнаруженные аномалии")
            st.markdown("""
            Аномалии — это отклонения в финансовых данных, которые требуют особого внимания.
            Они могут быть статистическими (резкие изменения показателей) или связаны с нарушением бизнес-логики.
            """)
            
            if anomalies:
                st.warning(f"Обнаружено **{len(anomalies)}** аномалий в финансовых данных")
                
                for idx, anomaly in enumerate(anomalies):
                    with st.expander(f"{'🔴' if anomaly['severity'] == 'high' else '🟠'} {anomaly['indicator']} ({anomaly['year']}) - {anomaly['type']}"):
                        st.markdown(f"**Тип аномалии:** {anomaly['type']}")
                        st.markdown(f"**Значение:** {anomaly['value']:,.0f} тыс. руб.")
                        if 'z_score' in anomaly:
                            st.markdown(f"**Z-score:** {anomaly['z_score']:.2f}")
                        st.markdown(f"**Описание:** {anomaly['description']}")
                
                # Визуализация аномалий
                fig_anomaly = plot_anomaly_visualization(df, anomalies)
                if fig_anomaly:
                    st.plotly_chart(fig_anomaly, use_container_width=True)
            else:
                st.success("✅ Аномалий, требующих внимания, не обнаружено")
        
        with tab5:
            st.header("💡 Финансовые коэффициенты")
            st.markdown("""
            Финансовые коэффициенты позволяют оценить различные аспекты финансового состояния компании:
            - **Ликвидность** — способность погашать краткосрочные обязательства
            - **Рентабельность** — эффективность использования ресурсов
            - **Финансовая устойчивость** — зависимость от заемных средств
            """)
            
            if ratios:
                # Выводим таблицу с коэффициентами
                ratios_df = pd.DataFrame([
                    {
                        'Коэффициент': name,
                        'Значение': data['value'],
                        'Норматив': data['norm'],
                        'Оценка': data['interpretation']
                    } for name, data in ratios.items()
                ])
                
                st.dataframe(
                    ratios_df.style.format({
                        'Значение': '{:.3f}',
                        'Норматив': '{:.3f}'
                    }),
                    hide_index=True,
                    use_container_width=True
                )
                
                # Визуализация коэффициентов
                fig_ratios = plot_financial_ratios(ratios)
                st.plotly_chart(fig_ratios, use_container_width=True)
                
                # Анализ коэффициентов
                st.subheader("Интерпретация ключевых коэффициентов")
                
                # Ликвидность
                st.markdown("#### 💧 Ликвидность")
                liquidity_ratios = ['Текущая ликвидность', 'Быстрая ликвидность', 'Абсолютная ликвидность']
                for ratio in liquidity_ratios:
                    if ratio in ratios:
                        r = ratios[ratio]
                        st.markdown(f"**{ratio}:** {r['value']:.3f} (норматив: {r['norm']:.3f}) — {r['interpretation']}")
                
                # Рентабельность
                st.markdown("#### 📈 Рентабельность")
                profitability_ratios = ['ROA', 'ROE', 'Маржа чистой прибыли']
                for ratio in profitability_ratios:
                    if ratio in ratios:
                        r = ratios[ratio]
                        st.markdown(f"**{ratio}:** {r['value']:.3f} (норматив: {r['norm']:.3f}) — {r['interpretation']}")
                
                # Финансовая устойчивость
                st.markdown("#### ⚖️ Финансовая устойчивость")
                stability_ratios = ['Коэффициент автономии']
                for ratio in stability_ratios:
                    if ratio in ratios:
                        r = ratios[ratio]
                        st.markdown(f"**{ratio}:** {r['value']:.3f} (норматив: {r['norm']:.3f}) — {r['interpretation']}")
            else:
                st.warning("Не удалось рассчитать финансовые коэффициенты из-за недостатка данных.")
        
        # Экспорт результатов
        st.markdown("---")
        st.header("📤 Экспорт результатов")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Кнопка для скачивания обработанных данных
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 Скачать данные в CSV",
                data=csv,
                file_name=f'financial_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv'
            )
        
        with col2:
            # Кнопка для скачивания PDF-отчета
            if st.button("📄 Сгенерировать PDF-отчет"):
                with st.spinner('Генерация PDF-отчета...'):
                    pdf_buffer = generate_pdf_report(
                        df, ratios, horizontal_df, 
                        vertical_asset_df, vertical_liability_df, 
                        anomalies
                    )
                    st.download_button(
                        label="📥 Скачать PDF-отчет",
                        data=pdf_buffer,
                        file_name=f'financial_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
                        mime='application/pdf'
                    )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>© 2023 Финансовый анализатор ООО 'Агрисовгаз' | Данные с сайта <a href="https://www.list-org.com" target="_blank">list-org.com</a></p>
</div>
""", unsafe_allow_html=True)