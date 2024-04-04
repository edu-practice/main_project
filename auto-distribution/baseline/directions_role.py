import pandas as pd


def students_roles(df):
    roles = {
        "Выберете интересующие Вас роли, в  IT [Бизнес и системный анализ]": "system or business analyst",
        "Выберете интересующие Вас роли, в  IT [Дизайн UX / UI и проектирование интерфейсов]": "ux/ui",
        "Выберете интересующие Вас роли, в  IT [Анализ и инженерия данных]": "da or de",
        "Выберете интересующие Вас роли, в  IT [Backend - разработка]": "backend developer",
        "Выберете интересующие Вас роли, в  IT [Frontend - разработка]": "frontend developer",
        "Выберете интересующие Вас роли, в  IT [Тестирование и обеспечение качества]": "qa",
        "Выберете интересующие Вас роли, в  IT [Развертывание и внедрение]": "implementation",
        "Выберете интересующие Вас роли, в  IT [Управление командой / проектом]": "pm",
    }

    data = df
    data["roles"] = [[] for _ in range(len(data))]
    roles_columns = list(roles.keys())
    new_roles = list(roles.values())
    roles_columns.append("Единая учетная запись СПбГУ (например, ST000000)")
    roles_columns.append("Year")
    df_roles = data[roles_columns]
    students = []
    df_roles.rename(columns=roles, inplace=True)
    df_roles = df_roles.fillna(0)
    df_roles = df_roles.reset_index()

    for index, student_df in df_roles.iterrows():
        student = dict()
        student["st"] = student_df["Единая учетная запись СПбГУ (например, ST000000)"]
        student["year"] = student_df["Year"]
        student["roles"] = []
        for column in new_roles:
            if int(student_df[column]) > 3:
                student["roles"].append(column.lower())
        data.at[index, "roles"] = student["roles"]
        students.append(student)

    return data, students


def directions_roles(df):
    directions = {
        "Выберете интересные для вас направление проекта (в направлении проекта могут быть все роли, указанные выше) [Разработка веб-сервисов (сайты, сервисы)]": "Web",
        "Выберете интересные для вас направление проекта (в направлении проекта могут быть все роли, указанные выше) [Анализ текстов и поисковые движки]": "NLP",
        "Выберете интересные для вас направление проекта (в направлении проекта могут быть все роли, указанные выше) [Анализ изображений / видео]": "CV",
        "Выберете интересные для вас направление проекта (в направлении проекта могут быть все роли, указанные выше) [Анализ временных рядов]": "Time Series",
        "Выберете интересные для вас направление проекта (в направлении проекта могут быть все роли, указанные выше) [Анализ табличных данных]": "DS",
        "Выберете интересные для вас направление проекта (в направлении проекта могут быть все роли, указанные выше) [Робототехника (оборудование, теория управления, техническое зрение, интерфейсы)]": "Robotics",
        "Выберете интересные для вас направление проекта (в направлении проекта могут быть все роли, указанные выше) [Gamedev]": "GameDev",
        "Если в предыдущем вопросе для Вас не было интересного направления деятельности, расскажите нам об области, в которой Вы хотите развиваться": "Other",
    }

    other = {
        "Разработка android приложений": ["Mobile Development"],
        "Звуковой анализ (спектральный, кепстральный), разработка музыкального программного обеспечения, разработка всевозможных мобильных приложений под iOS/iPadOS на Swift, разработка всевозможных приложений и информационных систем под macOS на Swift": [
            "Mobile Development",
            "DS",
        ],
        "STT, TTS": ["DS"],
        "Мультиагентные системы и обучение с подкреплением. Генетические алгоритмы": ["DS"],
        "К первому вопросу: работаю продуктовым аналитиком, потому интересен анализ данных и взаимодействия с пользователями с применением ключевых метрик.": [
            "Data Analysis"
        ],
        "Области интересные, но также хотчу добавить Мобильную Разработку": ["Mobile Development"],
        "android разработка": ["Mobile Development"],
        "Data analysis, engineering": ["Data Analysis", "Data Engeneering"],
        "Промышленная роботехника и применение нейросетей для задач точного измерения": ["Robotics"],
        "Анализ речи. Звуковые данные": ["DS", "Data Analysis"],
        "Дополнительно к предыдущему - цифровая обработка сигналов": ["DS"],
        "Разработка мобильных приложений под android": ["Mobile Development"],
        "Data engineer": ["Data Engeneering"],
        "Мобильная разработка (Android, Kotlin Multiplatform)": ["Mobile Development"],
        "Разработка API (django, fastapi...)": ["API"],
        "Биоинформатика, анализ биологических данных": ["DS", "Data Analysis"],
        "Мобильная Разработка Android IOS Flutter": ["Mobile Development"],
        "Меня интересует цифровая схемотехника, архитектура компьютера": ["low_level development"],
        "Пентест; системное программирование; проектирование программного обеспечения.": ["low_level development"],
        "Аналитик данных": ["Data Analysis"],
        "Хочу развиваться в области анализа данных,за лето разобрался с основами и планирую закрепить изученное и  получить опыт и новые знания в учебной практике": [
            "Data Analysis"
        ],
        "Нарративный дизайнер": ["Design"],
        "Android разработка": ["Mobile Development"],
        "Глубокое обучение": ["DL"],
        "Очень хочу развиваться в сфере дизайна": ["Design"],
        "В дополнение к вебу - мобильная разработка. \nХотелось бы уделить больше времени не рутинной реализации, а продумыванию оптимальной архитектуры, удобных интерфейсов и внутрикомандного взаимодействия.": [
            "Mobile Development"
        ],
        "Хотел бы писать полезные людям приложения под iOS, MacOS, AppleWatch и под остальные девайсы Apple. Под полезными подразумеваю: помощь в жизни, продуктивности, в лайф-стайле и тд. Не уверен что сверху мог где-то это отметить.": [
            "Mobile Development"
        ],
        "Системное программирование (под linux), низкоуровневое программирование": ["low_level development"],
        'В предыдущих вопросах использовал "не знаком" как "не против". В анализе только в качестве визуализации.\n\nВообще чем-то в районе инструментов визуального программирования я бы занялся.': [
            "Data Analysis"
        ],
        "Хотела попробовать себя в сферах связанных с медициной и биологией, так как мне достаточно интересны гематология и генетика. Также моя выпускная работа будет скорее всего связана с медико-биологической статистикой. Но также было бы интересно попробовать себя и в других направлениях.": [
            "Data Analysis"
        ],
        "Компьютерная графика, разработка языков программирования": ["Design", "programming language development"],
        None: "",
    }

    data = df
    data["directions"] = [[] for _ in range(len(data))]
    directions_columns = list(directions.keys())
    new_columns = list(directions.values())
    directions_columns.append("Единая учетная запись СПбГУ (например, ST000000)")
    directions_columns.append("Year")
    df_directions = data[directions_columns]
    df_directions.rename(columns=directions, inplace=True)
    df_directions = df_directions.fillna(0)
    df_directions["Other"] = df_directions["Other"].map(other)
    df_directions["Other"] = df_directions["Other"].fillna("0")
    df_directions = df_directions.reset_index()

    for index, student_df in df_directions.iterrows():
        student = dict()
        student["directions"] = []
        for column in new_columns:
            if column != "Other" and int(student_df[column]) > 1:
                student["directions"].append(column)
            if column == "Other" and student_df["Other"] != "0":
                for d in student_df["Other"]:
                    student["directions"].append(d)
        data.at[index, "directions"] = student["directions"]

    data_with_d_r, students = students_roles(data)

    return data_with_d_r, students
