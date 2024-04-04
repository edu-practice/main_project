import streamlit as st
import pandas as pd
import numpy as np
import baseline as base
import coding_and_double_cleaner as cc
import score
import directions_role as dr


def f(data):
    if isinstance(data, list):
        if len(data) == 0:
            return ""
        elif isinstance(data[0], list):
            for i in range(len(data)):
                data[i] = " ".join([str(x) for x in data[i]])
            return data
        else:
            return data
    else:
        return data


def style(df):
    rename_c = {"name": "Название", "directions": "Направления", "team": "Команда", "status": "Статус"}

    for column in df.columns:
        if df[column].dtype == "object":
            df[column] = df[column].apply(lambda x: f(x))
    df = df.rename(columns=rename_c)
    return df


# Title of the app
st.title("Распределение команд")

# File uploader widget
file1 = st.file_uploader("Загрузите Excel таблицу с проектами", type=["xlsx"])
file2 = st.file_uploader("Загрузите Excel таблицу со студентами", type=["xlsx"])
team_size = st.text_input("Введите размер команд или оставьте поле пустым")

# Check if a file has been uploaded
if file1 is not None and file2 is not None:
    # Read the excel file
    df_projects = pd.read_excel(file1)
    # Read the excel file
    df_students = pd.read_excel(file2)
    df_students = cc.code_clean(df_students)
    df_students, _ = score.skills_score(df_students)
    df_students, _ = dr.directions_roles(df_students)

    # Display the DataFrame
    st.write("### Датасет проектов:")
    st.write(df_projects)
    # Display the DataFrame
    st.write("### Датасет студентов:")
    st.write(df_students)
    if team_size == "":
        # data preparation
        students, projects = base.data_preparation(df_students, df_projects)
        directions = base.get_directions_of_projects(projects)
        distributed_students, distributed_projects = base.distribute_students(directions, students, projects)
    else:
        students, projects = base.data_preparation(df_students, df_projects)
        directions = base.get_directions_of_projects(projects)
        distributed_students, distributed_projects = base.distribute_students(
            directions, students, projects, int(team_size)
        )

    df_new = pd.DataFrame.from_records(distributed_projects)
    st.write("### Распределение по командам:")
    st.write(style(df_new))

    st.write("### Поменять студентов между двумя командами: ")
    PS_1 = st.text_input("Введите название 1-го проекта и ST студента через ;")
    PS_2 = st.text_input("Введите название 2-го проекта и ST студента через ;")
    if (len(PS_1) != 0 and len(PS_2) != 0) and (";" in PS_1 and ";" in PS_2):
        project1 = PS_1.split(";")[0].strip()
        student1 = PS_1.split(";")[1].strip()
        st.write(project1, student1)

        project2 = PS_2.split(";")[0].strip()
        student2 = PS_2.split(";")[1].strip()
        st.write(project2, student2)
        result = base.student_exchange(project1, student1, project2, student2, distributed_projects)
        print("here ", result)
        if result == -1:
            st.write(Exception("""Ошибка, проверьте корректность ST студента"""))
        elif result == -2:
            st.write(Exception("""Ошибка, проверьте корректность названия проекта"""))
        else:
            df_new_exchanged = pd.DataFrame.from_records(result)
            st.write("### Изменения внесены: ")
            st.write(style(df_new_exchanged))

    st.write("### Добавить новоприбывшего студента: ")
    new_student_df = st.file_uploader("Загрузите Excel таблицу с новым студентом", type=["xlsx"])
    project_for_new_student = st.text_input("Введите название проекта для студента или оставьте поля пустым")
    if new_student_df is not None:
        new_student = pd.read_excel(new_student_df)
        new_student = cc.code_clean(new_student)
        new_student, _ = score.skills_score(new_student)
        new_student, _ = dr.directions_roles(new_student)
        new_student = base.df_students(new_student)
        # if len(project_for_new_student) == 0:
        result1 = base.add_new_student(distributed_projects, new_student)
        # else:
        #   result1 = base.add_new_student(distributed_projects, new_student, project_for_new_student)
        if result1 == -1:
            st.write(Exception("""Ошибка"""))
        else:
            st.write("### Изменения внесены: ")
            df_new_1 = pd.DataFrame.from_records(result1)
            df_new_1 = style(df_new_1)
            for col in df_new_1.columns:
                if df_new_1[col].dtype == "object":
                    df_new_1[col] = df_new_1[col].astype(str)
            st.write(df_new_1)
