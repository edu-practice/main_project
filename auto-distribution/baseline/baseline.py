import pandas as pd
import numpy as np
import copy


# add version with pre-selected students
def df_students(df):
    students = []
    df = df.reset_index()

    for _, student_df in df.iterrows():
        student = dict()
        student["st"] = student_df["Единая учетная запись СПбГУ (например, ST000000)"]
        student["year"] = student_df["Year"]
        student["score"] = student_df["score"]
        student["season"] = student_df["Season"]
        student["directions"] = student_df["directions"]
        student["roles"] = student_df["roles"]

        students.append(student)

    return students


def add_new_student(distributed_projects, student=None, TheProject=None):
    if student is None:
        return -1
    else:
        for st in student:
            if TheProject is not None:
                for project in distributed_projects:
                    if project["name"] == TheProject:
                        project["team"].append(st)
                        return distributed_projects
            else:
                candidates = [
                    p
                    for p in distributed_projects
                    if len(set(p["directions"]).intersection(st["directions"])) > 0 and p["status"] == "incomplete"
                ]
                if len(candidates) != 0:
                    looser = candidates[0]
                    index = 0
                    for p in candidates:
                        if p["team_mean_score"] < looser["team_mean_score"]:
                            looser = p
                            index = candidates.index(p)
                    candidates[index]["team"].append([st["st"], st["score"], st["year"], st["season"]])
                    n = len(candidates[index]["team"])
                    candidates[index]["team_mean_score"] = (
                        candidates[index]["team_mean_score"] * (n - 1) + st["score"]
                    ) / n
                    candidates[index]["remainder"] -= 1
                    if candidates[index]["remainder"] == 0:
                        candidates[index]["status"] = "complete"
                    return candidates
                else:
                    looser = distributed_projects[0]
                    index = 0
                    for p in distributed_projects:
                        if p["team_mean_score"] < looser["team_mean_score"]:
                            looser = p
                            index = distributed_projects.index(p)
                    distributed_projects[index]["team"].append([st["st"], st["score"], st["year"], st["season"]])
                    n = len(distributed_projects[index]["team"])
                    distributed_projects[index]["team_mean_score"] = (
                        distributed_projects[index]["team_mean_score"] * (n - 1) + st["score"]
                    ) / n
                    distributed_projects[index]["remainder"] -= 1
                    if distributed_projects[index]["remainder"] == 0:
                        distributed_projects[index]["status"] = "complete"
                    return distributed_projects


def data_preparation(df_students, df_projects):
    students = []
    students_df = df_students.reset_index()

    for _, student_df in students_df.iterrows():
        student = dict()
        student["st"] = student_df["Единая учетная запись СПбГУ (например, ST000000)"]
        student["year"] = student_df["Year"]
        student["season"] = student_df["Season"]
        student["score"] = student_df["score"]
        student["directions"] = student_df["directions"]
        student["roles"] = student_df["roles"]
        students.append(student)

    projects = []
    projects_df = df_projects.reset_index()
    for _, project_df in projects_df.iterrows():
        project = dict()
        project["name"] = project_df["Проект"]
        project["year"] = project_df["Год"]
        project["season"] = project_df["Сезон"]
        d = []
        for w in project_df["Направление"].split(sep=","):
            d.append(w.strip())
        project["directions"] = d
        c = []
        for w in project_df["Состав команды"].split(sep=","):
            if ":" in w:
                project["team"] = []
                student_st = w.split(sep=":")[1].strip()
                for s in students:
                    if s["st"] == student_st:
                        s["assigned"] = True
                        project["team"].append(s)
                        role = w.split(sep=":")[0]
                        project[role.strip().lower()] = []
                        project[role.strip().lower()].append([s["st"], s["score"], s["year"], s["season"]])
                        break
                c.append(role.strip().lower())
            else:
                project[w.strip().lower()] = []
                c.append(w.strip().lower())
        project["compound"] = c

        projects.append(project)

    return students, projects


def student_exchange(project1, student_st1, project2, student_st2, distprojects):
    distributed_projects_new = copy.deepcopy(distprojects)
    student1 = []
    student2 = []
    p1_index = 0
    p2_index = 0
    student1_role = ""
    student2_role = ""
    i = 0
    for project in distributed_projects_new:
        if project["name"] == project1:
            p1_index = distributed_projects_new.index(project)
            p_1 = project
            for student in project["team"]:
                if student.split(" ")[0] == student_st1:
                    student1 = student
                    project["team"].remove(student)
                    for role in project["compound"]:
                        if student1 in project[role]:
                            project[role].remove(student1)
                            student1_role = role
                            break
                    break
            if len(student1) == 0:
                return -1
            i += 1

        if project["name"] == project2:
            p2_index = distributed_projects_new.index(project)
            p_2 = project
            for student in project["team"]:
                if student.split(" ")[0] == student_st2:
                    student2 = student
                    project["team"].remove(student)
                    for role in project["compound"]:
                        if student2 in project[role]:
                            project[role].remove(student2)
                            student2_role = role
                            break
                    break
            if len(student2) == 0:
                return -1
            i += 1

        if i == 2:
            break

    if (p1_index == 0) | (p2_index == 0):
        return -2

    if len(student1_role) != 0 and len(student2) != 0:
        p_1["team"].append(student2)
        p_1[student1_role].append([student2[0], student2[1], student2[2]])
        distributed_projects_new[p1_index] = p_1
    elif len(student1_role) == 0 and len(student2) != 0:
        p_1["team"].append(student2)
        distributed_projects_new[p1_index] = p_1

    if len(student2_role) != 0 and len(student1) != 0:
        p_2["team"].append(student1)
        p_2[student2_role].append([student1[0], student1[1], student1[2]])
        distributed_projects_new[p2_index] = p_2
    elif len(student2_role) == 0 and len(student1) != 0:
        p_2["team"].append(student1)
        distributed_projects_new[p2_index] = p_2

    return distributed_projects_new


def get_roles(students):
    roles = []
    for student in students:
        for role in student["roles"]:
            roles.append(role.lower())
    roles = set(roles)
    return roles


def get_directions_of_projects(projects):
    directions = []
    for project in projects:
        for direction in project["directions"]:
            directions.append(direction.lower())
    directions = set(directions)
    return directions


def create_dict_of_students_by_direction(directions, students):
    directions_students = {direction: [] for direction in directions}
    for student in students:
        for direction in student["directions"]:
            if direction.lower() in directions:
                directions_students[direction.lower()].append(student)
    return directions_students


def avg_score(students):
    scores = [student["score"] for student in students]
    if len(scores) == 0:
        return None
    return sum(scores) / len(scores)


# Распределение по остаточному признаку


def distribute_remaining_students(students, projects, avg):
    assigned_students = []
    for student in students:
        if ("assigned" in student.keys()) and (student["assigned"] == True):
            student["avg_proj"] = student["score"] / avg
        else:
            student["avg_proj"] = student["score"] / avg
            student["assigned"] = False

    remaining_students = [
        student for student in students if ("assigned" in student.keys()) and (student["assigned"] == False)
    ]
    remaining_students.sort(key=lambda x: x["avg_proj"])
    for project in projects:
        remaining_roles = project["remaining_roles"]
        while len(remaining_students) > 0 and project["remainder"] > 0 and len(remaining_roles) > 0:
            for role in remaining_roles:
                if len(project[role]) == project["compound"].count(role):
                    remaining_roles.remove(role)
                    project["remainder"] -= 1
                    break

                student = remaining_students.pop(len(remaining_students) // 2)
                project[role].append([student["st"], student["score"], student["year"], student["season"]])
                project["team"].append([student["st"], student["score"], student["year"], student["season"]])
                project["remainder"] -= 1
                student["assigned"] = True
                assigned_students.append(student)  # Добавить студента в список назначенных
                remaining_roles.remove(role)
                break

    for project in projects:
        while project["remainder"] > 0 and len(remaining_students) > 0:
            student = remaining_students.pop(len(remaining_students) // 2)
            project["team"].append([student["st"], student["score"], student["year"], student["season"]])
            project["remainder"] -= 1
            student["assigned"] = True
            assigned_students.append(student)

        if project["remainder"] == 0:
            project["status"] = "complete"

        project["team_mean_score"] = np.mean([s[1] for s in project["team"]])

    return students, projects


# v6


def distribute_students(directions, students, projects, team_size=False):
    direction_students = create_dict_of_students_by_direction(directions, students)
    assigned_students = []
    avg = avg_score(students)
    students_without_direction = [student for student in students if len(student["directions"]) == 0]
    students_without_roles = [student for student in students if len(student["roles"]) == 0]
    projects_distributed = projects.copy()

    for project in projects_distributed:
        if team_size:
            size = team_size
        else:
            size = len(project["compound"])
        project["team"] = []
        remaining_roles = project["compound"].copy()
        candidates = []

        for direction in project["directions"]:
            candidates.extend(direction_students[direction.lower()])

        for candidate in candidates:
            if ("assigned" in candidate.keys()) and (candidate["assigned"] == True):
                candidate["avg_proj"] = candidate["score"] / avg
            else:
                candidate["avg_proj"] = candidate["score"] / avg
                candidate["assigned"] = False

        candidates.sort(key=lambda x: x["avg_proj"])

        while size > 0 and len(candidates) > 0:
            student = candidates.pop(len(candidates) // 2)
            # Проверить, что студент не был уже назначен и не находится в списке assigned_students
            if not student["assigned"] and student not in assigned_students:
                for role in remaining_roles:
                    if len(project[role]) == project["compound"].count(role):
                        remaining_roles.remove(role)
                        size -= 1
                        break

                    if role in student["roles"]:
                        project[role].append([student["st"], student["score"], student["year"], student["season"]])
                        project["team"].append([student["st"], student["score"], student["year"], student["season"]])
                        size -= 1
                        student["assigned"] = True
                        assigned_students.append(student)  # Добавить студента в список назначенных
                        remaining_roles.remove(role)
                        break

        """team_avg_score = avg_score(project['team'])

      while size > 0 and len(candidates) > 0:
            candidates.sort(key=lambda x: abs(x['score'] - team_avg_score))
            student = candidates.pop(len(candidates)//2) #Выбирается медиана
            if not student['assigned'] and student not in assigned_students:
                project['team'].append(student)
                size -= 1
                student['assigned'] = True
                assigned_students.append(student)
"""
        while size > 0 and len(students_without_direction) > 0:
            student = students_without_direction.pop(len(students_without_direction) // 2)
            for role in remaining_roles:
                if len(project[role]) == project["compound"].count(role):
                    remaining_roles.remove(role)
                    size -= 1
                    break

                if role in student["roles"]:
                    project["team"].append([student["st"], student["score"], student["year"], student["season"]])
                    project[role].append([student["st"], student["score"], student["year"], student["season"]])
                    remaining_roles.remove(role)
                    size -= 1

        while size > 0 and len(students_without_roles) > 0:
            student = students_without_roles.pop(len(students_without_roles) // 2)
            for role in remaining_roles:
                if len(project[role]) == project["compound"].count(role):
                    remaining_roles.remove(role)
                    size -= 1
                    break

                project["team"].append([student["st"], student["score"], student["year"], student["season"]])
                project[role].append([student["st"], student["score"], student["year"], student["season"]])
                remaining_roles.remove(role)
                size -= 1

        if size > 0:
            project["status"] = "incomplete"
            project["remaining_roles"] = remaining_roles
            project["remainder"] = size
        else:
            project["status"] = "complete"
            project["remaining_roles"] = []
            project["remainder"] = 0

    students, projects_distributed = distribute_remaining_students(students, projects_distributed, avg)

    for project in projects_distributed:
        print(
            f"Project: {project['name']}, {project['directions']}, {project['status']}, {project['team_mean_score']}, {project['compound']}, {len(project['team'])}"
        )
        print("Assigned Students:")
        for p in set(project["compound"]):
            print(f"- {p}: {project[p]}")
        print()

    return students, projects_distributed
