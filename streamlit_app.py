import streamlit as st
import pandas as pd
import sqlite3

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

# Интерфейс Streamlit
st.title("Расписание занятий")

# Загружаем группы и предлагаем выбор
groups = load_groups()
group_names = dict(zip(groups['название'], groups['группа_id']))
selected_group = st.selectbox("Выберите группу:", list(group_names.keys()))

# Загружаем и отображаем расписание для выбранной группы
if selected_group:
    group_id = group_names[selected_group]
    schedule = load_schedule(group_id)

    if schedule.empty:
        st.write("Для выбранной группы расписание отсутствует.")
    else:
        st.write(f"Расписание для группы {selected_group}:")
        st.dataframe(schedule)

