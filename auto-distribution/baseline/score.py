import pandas as pd
import numpy as np
import re


def get_element_safely(lst, index=0, default=1):
    if 0 <= index < len(lst):
        return int(lst[index])
    else:
        return default


def evaluate_skills(skills_dict):
    if not skills_dict:
        return 0

    score = list(skills_dict.values())
    total_score = sum(score)
    average_score = total_score / len(skills_dict)
    return average_score


def skills_score(df):
    pattern1 = r"\n?([a-zA-Zс+.#]+)"
    pattern2 = r"\d"
    data = df
    data["score"] = None
    data["hard_skills_score"] = None
    data["soft_skills_score"] = None
    data["analytics_skills_score"] = None
    data["knowladges_skills_score"] = None
    df["Year"] = df["Отметка времени"].dt.year
    df["Season"] = np.where(df["Отметка времени"].dt.month > 7, "Осень", "Весна")

    soft_skills_columns = [col for col in df.columns if "SoftSkills" in col]
    analytics_skills_columns = [col for col in df.columns if "Аналитические" in col]
    knowladges_skills_columns = [col for col in df.columns if "знания в области" in col]
    students = []
    for _, student_df in data.iterrows():
        student = dict()
        student["st"] = student_df["Единая учетная запись СПбГУ (например, ST000000)"]
        student["year"] = student_df["Year"]
        student["season"] = student_df["Season"]

        student["languages"] = {
            re.findall(pattern1, x)[0]: get_element_safely(re.findall(pattern2, x))
            for x in str(student_df["Языки программирования (например: C++, Python, Java, etc)"])
            .lower()
            .split(sep="\n")
            if (pd.notna(x)) and (re.findall(pattern1, x) != [])
        }
        student["languages_score"] = evaluate_skills(student["languages"])

        student["ci_cd"] = {
            re.findall(pattern1, x)[0]: get_element_safely(re.findall(pattern2, x))
            for x in str(student_df["Инструменты CI / CD (например: Jenkins, Travis CI, Docker, etc)"])
            .lower()
            .split(sep="\n")
            if (pd.notna(x)) and (re.findall(pattern1, x) != [])
        }
        student["ci_cd_score"] = evaluate_skills(student["ci_cd"])

        student["analysis"] = {
            re.findall(pattern1, x)[0]: get_element_safely(re.findall(pattern2, x))
            for x in str(
                student_df[
                    "Инструменты для проектирования, бизнес и системного анализа (например: BPMN, UML, Archimate, ARIS etc)"
                ]
            )
            .lower()
            .split(sep="\n")
            if (pd.notna(x)) and (re.findall(pattern1, x) != [])
        }
        student["analysis_score"] = evaluate_skills(student["analysis"])

        student["test"] = {
            re.findall(pattern1, x)[0]: get_element_safely(re.findall(pattern2, x))
            for x in str(student_df["Инструменты для тестирования  (например: GTests, Selenium, Gatling, pytest etc)"])
            .lower()
            .split(sep="\n")
            if (pd.notna(x)) and (re.findall(pattern1, x) != [])
        }
        student["test_score"] = evaluate_skills(student["test"])

        student["frameworks"] = {
            re.findall(pattern1, x)[0]: get_element_safely(re.findall(pattern2, x))
            for x in str(
                student_df[
                    "Библиотеки и фреймворки для различных направлений использования (например: Qt, Numpy, Weka, Angular, PyTorch, etc)"
                ]
            )
            .lower()
            .split(sep="\n")
            if (pd.notna(x)) and (re.findall(pattern1, x) != [])
        }
        student["frameworks_score"] = evaluate_skills(student["frameworks"])

        student["dev"] = {
            re.findall(pattern1, x)[0]: get_element_safely(re.findall(pattern2, x))
            for x in str(student_df["Инструменты для разработки ПО - например: VS Code, PyCharm, Git, etc)"])
            .lower()
            .split(sep="\n")
            if (pd.notna(x)) and (re.findall(pattern1, x) != [])
        }
        student["dev_score"] = evaluate_skills(student["dev"])

        student["hard_skills_score"] = np.round(
            student["dev_score"] * 1 / 6
            + student["frameworks_score"] * 1 / 6
            + student["languages_score"] * 1 / 6
            + student["ci_cd_score"] * 1 / 6
            + student["test_score"] * 1 / 6
            + student["analysis_score"] * 1 / 6,
            1,
        )
        student["soft_skills_score"] = np.round(student_df[soft_skills_columns].fillna(0).mean(), 1)
        student["analytics_skills_score"] = np.round(student_df[analytics_skills_columns].fillna(0).mean(), 1)
        student["knowladges_skills_score"] = np.round(student_df[knowladges_skills_columns].fillna(0).mean(), 1)

        student["score"] = np.round(
            student["hard_skills_score"]
            + student["soft_skills_score"]
            + student["analytics_skills_score"]
            + student["knowladges_skills_score"],
            1,
        )

        students.append(student)

        data.loc[
            (data["Единая учетная запись СПбГУ (например, ST000000)"] == student["st"])
            & (data["Year"] == int(student["year"]))
            & (data["Season"] == student["season"]),
            "score",
        ] = student["score"]
        data.loc[
            (data["Единая учетная запись СПбГУ (например, ST000000)"] == student["st"])
            & (data["Year"] == int(student["year"]))
            & (data["Season"] == student["season"]),
            "hard_skills_score",
        ] = student["hard_skills_score"]
        data.loc[
            (data["Единая учетная запись СПбГУ (например, ST000000)"] == student["st"])
            & (data["Year"] == int(student["year"]))
            & (data["Season"] == student["season"]),
            "soft_skills_score",
        ] = student["soft_skills_score"]
        data.loc[
            (data["Единая учетная запись СПбГУ (например, ST000000)"] == student["st"])
            & (data["Year"] == int(student["year"]))
            & (data["Season"] == student["season"]),
            "analytics_skills_score",
        ] = student["analytics_skills_score"]
        data.loc[
            (data["Единая учетная запись СПбГУ (например, ST000000)"] == student["st"])
            & (data["Year"] == int(student["year"]))
            & (data["Season"] == student["season"]),
            "knowladges_skills_score",
        ] = student["knowladges_skills_score"]

    return data, students
