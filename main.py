import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# Конфигурация курса
start_date = datetime(2025, 3, 24)
end_date = datetime(2025, 10, 10)
hours_per_day = 4
weekdays = {0, 1, 2, 3, 4}  # Рабочие дни (0 - Пн, 4 - Пт)

# Определяем текущую дату
current_date = datetime.now()

# Определяем текущий уровень языка
levels = [
    ("A0", start_date),
    ("A1.1", start_date + timedelta(days=20)),
    ("A1.2", start_date + timedelta(days=40)),
    ("A2.1", start_date + timedelta(days=60)),
    ("A2.2", start_date + timedelta(days=80)),
    ("B1.1", start_date + timedelta(days=100)),
    ("B1.2", start_date + timedelta(days=120)),
    ("B1", end_date),
]

current_level = "A0"
for level, level_date in levels:
    if current_date >= level_date:
        current_level = level

# Полное количество часов и расчёт прогресса
total_hours = sum(hours_per_day for d in pd.date_range(start=start_date, end=end_date) if d.weekday() in weekdays)
past_hours = sum(hours_per_day for d in pd.date_range(start=start_date, end=min(current_date, end_date)) if d.weekday() in weekdays)
remaining_hours = total_hours - past_hours
progress = (past_hours / total_hours) * 100 if total_hours > 0 else 0

# Функция для вычисления градиентного цвета
def interpolate_color(start_color, mid_color, end_color, progress):
    if progress < 50:
        r1, g1, b1 = start_color
        r2, g2, b2 = mid_color
        factor = progress / 50
    else:
        r1, g1, b1 = mid_color
        r2, g2, b2 = end_color
        factor = (progress - 50) / 50

    r = int(r1 + (r2 - r1) * factor)
    g = int(g1 + (g2 - g1) * factor)
    b = int(b1 + (b2 - b1) * factor)
    
    return f"rgb({r},{g},{b})"

# Определение состояния курса (ещё не начался, идёт, завершён)
if current_date < start_date:
    status_message = "Курс ещё не начался!"
    battery_color = "rgb(150, 150, 150)"  # Серый цвет
    battery_width = 5
    progress = 0
    remaining_hours = total_hours
    current_level = "A0"
elif current_date >= end_date:
    status_message = "Курс завершён! Поздравляем! 🎉"
    battery_color = "rgb(76, 175, 80)"  # Полностью зелёный
    battery_width = 120  # Теперь ширина не превышает границы батареи
    progress = 100
    remaining_hours = 0
    current_level = "B1"
else:
    status_message = f"Изучение идёт! Осталось {remaining_hours} часов."
    battery_color = interpolate_color((244, 67, 54), (255, 193, 7), (76, 175, 80), progress)
    battery_width = min(int(progress * 1.2), 120)  # Гарантируем, что ширина не выйдет за 120 пикселей

# SVG-анимация батарейки
battery_svg = f"""
<svg width="150" height="80" viewBox="0 0 150 80">
    <rect x="5" y="15" width="120" height="50" rx="8" ry="8" stroke="black" stroke-width="3" fill="none"/>
    <rect x="125" y="30" width="10" height="20" fill="black"/>
    <rect x="10" y="20" width="{battery_width}" height="40" rx="5" ry="5" fill="{battery_color}" />
</svg>
"""

# Интерфейс Streamlit
st.set_page_config(page_title="2025 - Прогресс изучения немецкого 🇩🇪", layout="wide")

st.title("⏳ Прогресс изучения немецкого языка 🇩🇪")

col1, col2 = st.columns([1, 2])

with col1:
    st.metric(label="📅 Дней до окончания", value=f"{max((end_date - current_date).days, 0)} дней")
    st.metric(label="🎓 Текущий уровень", value=current_level)
    st.markdown(f'<div style="text-align: center;">{battery_svg}</div>', unsafe_allow_html=True)
    st.info(status_message)

with col2:
    if current_date < end_date:
        st.subheader(f"Осталось {remaining_hours} часов из {total_hours}")
        st.progress(progress / 100)

# График прогресса (дорожная карта)
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=[lvl[1] for lvl in levels],
    y=[lvl[0] for lvl in levels],
    mode="lines+markers",
    line=dict(color="green", width=5),
    fill="tozeroy",
    name="Пройдено"
))

if current_date < end_date:
    fig.add_trace(go.Scatter(
        x=[lvl[1] for lvl in levels if lvl[1] > current_date],
        y=[lvl[0] for lvl in levels if lvl[1] > current_date],
        mode="lines+markers",
        line=dict(color="gray", width=2, dash="dash"),
        name="Осталось"
    ))

fig.update_layout(
    title="📈 Путь к B1: Ожидаемый прогресс изучения немецкого языка",
    xaxis_title="Дата",
    yaxis_title="Уровень языка",
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, categoryorder="array", categoryarray=[lvl[0] for lvl in levels]),
    template="plotly_white",
    height=500
)

st.plotly_chart(fig)
