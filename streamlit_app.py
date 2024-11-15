import streamlit as st
import pandas as pd
import sqlite3
import datetime

st.html('<head><script src="https://telegram.org/js/telegram-web-app.js"></script></head>')
# Подключение к базе данных SQLite
def get_connection():
    return sqlite3.connect("schedule.db")

# Функция для загрузки данных групп из базы данных
def load_groups():
    conn = get_connection()
    query = "SELECT группа_id, название FROM Группы"
    groups_df = pd.read_sql(query, conn)
    conn.close()
    return groups_df

# Функция для загрузки данных о днях недели из базы данных
def load_days_of_week():
    conn = get_connection()
    query = "SELECT день_id, название FROM Дни_недели ORDER BY день_id"
    days_df = pd.read_sql(query, conn)
    conn.close()
    return days_df

# Функция для загрузки расписания для выбранной группы
def load_schedule(group_id):
    conn = get_connection()
    query = """
    SELECT
        Дисциплины.название AS Дисциплина,
        Преподаватели.имя || ' ' || Преподаватели.фамилия AS Преподаватель,
        Время.время_начала || ' - ' || Время.время_окончания AS Время,
        Дни_недели.название AS День,
        Аудитории.номер AS Аудитория
    FROM Расписание
    JOIN Дисциплины ON Расписание.дисциплина_id = Дисциплины.дисциплина_id
    JOIN Преподаватели ON Расписание.преподаватель_id = Преподаватели.преподаватель_id
    JOIN Время ON Расписание.время_id = Время.время_id
    JOIN Дни_недели ON Расписание.день_id = Дни_недели.день_id
    JOIN Аудитории ON Расписание.аудитория_id = Аудитории.аудитория_id
    WHERE Расписание.группа_id = ?
    ORDER BY Дни_недели.день_id, Время.время_начала
    """
    schedule_df = pd.read_sql(query, conn, params=(group_id,))
    conn.close()
    return schedule_df

# Функция для получения текущего дня недели
def get_today_weekday():
    today = datetime.datetime.today().weekday()  # 0 - понедельник, 1 - вторник, ...
    return today

# Интерфейс Streamlit
st.title("Расписание занятий")

# Загружаем дни недели для выбора
days_of_week = load_days_of_week()

# Загружаем группы и предлагаем выбор
groups = load_groups()
group_names = dict(zip(groups['название'], groups['группа_id']))
selected_group = st.selectbox("Выберите группу:", list(group_names.keys()))

if selected_group:
    # Кнопка для отображения расписания
    show_button = st.button("Показать расписание")

    if show_button:
        group_id = group_names[selected_group]
        schedule = load_schedule(group_id)

        if schedule.empty:
            st.write("Ура, выходной!")
        else:
            st.write(f"Расписание для группы {selected_group}:")
            st.dataframe(schedule)
            st.dataframe(schedule, use_container_width=True, index=False)

    # Кнопка "Показать расписание на сегодня"
    show_today_button = st.button("Показать расписание на сегодня")

    if show_today_button:
        today = get_today_weekday()
        group_id = group_names[selected_group]
        schedule = load_schedule(group_id)

        # Фильтруем расписание по текущему дню
        today_day = days_of_week.iloc[today]['название']
        today_schedule = schedule[schedule['День'] == today_day]

        if today_schedule.empty:
            st.write("Ура, выходной!")
        else:
            st.write(f"Расписание для группы {selected_group} на сегодня ({today_day}):")
            st.dataframe(today_schedule)
            st.dataframe(schedule, use_container_width=True, index=False)

    # Выбор дня недели
    selected_day = st.selectbox("Выберите день недели:", list(days_of_week['название']))

    # Кнопка "Показать расписание на выбранный день"
    show_selected_day_button = st.button(f"Показать расписание на {selected_day}")

    if show_selected_day_button:
        group_id = group_names[selected_group]
        schedule = load_schedule(group_id)

        # Фильтруем расписание по выбранному дню
        selected_day_schedule = schedule[schedule['День'] == selected_day]

        if selected_day_schedule.empty:
            st.write("Ура, выходной!")
        else:
            st.write(f"Расписание для группы {selected_group} на {selected_day}:")
            st.dataframe(selected_day_schedule)
            st.dataframe(schedule, use_container_width=True, index=False)
