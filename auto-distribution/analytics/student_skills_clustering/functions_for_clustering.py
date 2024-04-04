import pandas as pd
import re

import seaborn as sns
import matplotlib.pyplot as plt

import numpy as np

from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans

from sklearn.decomposition import PCA


def extract_specific_features(file_name):
    techs = []
    with open(file_name, "r") as file:
        techs = file.read().splitlines()
    return techs

def collect_competency_matrix(new_df, tech_columns):
    # список, в котором будут храниться все уникальные технологии из разных файлов
    all_technologies = []

    # Пройдемся по всем файлам и добавим уникальные технологии в список
    file_paths = ["languages.txt", "frameworks.txt", "analysis_tools.txt", "CI_CD.txt", "dev_tools.txt",  "project_management_tools.txt", "test_tools.txt"]
    for file_path in file_paths:
        with open(file_path, "r") as file:
            technologies = file.read().splitlines()
            
            all_technologies.extend(technologies)

    # Удалить дубликаты 
    all_technologies = list(set(all_technologies))

    tech_df = pd.DataFrame(columns=all_technologies, index=range(len(new_df)))


    # Создать столбцы для каждой уникальной технологии и заполнить их нулями
    for tech in all_technologies:
        tech_df[tech] = 0

    def fill_tech_df_with_values(tech_df, column_name: str):
        for i, response in new_df.iterrows():
            competence_values = {}  # Создать пустой словарь для хранения значений компетенций студента

            # Регулярное выражение для извлечения технологий и оценок
            pattern = r"([a-zA-Z\-\+ # .\d]+) - (\d)" 
            
            # response_lower = response.lower()
            response_lower = response[column_name].lower()
            cleaned_response = response_lower.replace('\n', ',')
            cleaned_response = cleaned_response.replace('с', 'c')
            cleaned_response = cleaned_response.replace('c ++', "c++")
            cleaned_response = cleaned_response.replace('pyhton', 'python')
            
            # Найти все совпадения в ответе студента
            matches = re.findall(pattern, cleaned_response)
            
            if matches:
                for match in matches:
                    technology = match[0].strip().lower()
                    rating = int(match[1])
                    competence_values[technology] = rating
                    # print(technology, rating)
                
                for tech in all_technologies:
                    if tech_df.at[i, tech] == 0:
                        tech_df.at[i, tech] = competence_values.get(tech, 0)
                        
    # Применить функцию к каждому столбцу, содержащему данные о технологиях
    for column in tech_columns:  # tech_columns - список названий столбцов с данными о технологиях
        fill_tech_df_with_values(tech_df, column)   
    
    return tech_df

def drop_zero_columns(df):
    # Проверяем, какие колонки полностью состоят из нулевых значений
    zero_columns = df.columns[df.eq(0).all(axis=0)]
    print("Колонки с нулевыми значениями:", zero_columns.tolist())
    df = df.drop(zero_columns, axis=1)
    return df


def find_parameters_for_DBSCUN(start, end, n_points, data, min_size=5):
    # Create a list of eps values to test
    # eps_values = np.linspace(0.1, 10.0, 100)
    eps_values = np.linspace(start, end, n_points)

    # Create lists to store the number of clusters and outlier counts for each eps value
    n_clusters_values = []
    n_outliers_values = []

    # Iterate over eps values and compute the number of clusters and outliers for each
    for eps in eps_values:
        dbscan = DBSCAN(eps=eps, min_samples=min_size)
        cluster_labels = dbscan.fit_predict(data)
        
        # Count the number of clusters (excluding outliers, which are labeled as -1)
        n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        
        # Count the number of outliers (points labeled as -1)
        n_outliers = np.sum(cluster_labels == -1)
        
        n_clusters_values.append(n_clusters)
        n_outliers_values.append(n_outliers)

    # Plot the number of clusters and outliers for each eps value
    plt.figure(figsize=(12,10))

    plt.subplot(1, 2, 1)
    plt.plot(eps_values, n_clusters_values, marker='o', linestyle='-')
    plt.xlabel('Eps Value')
    plt.ylabel('Number of Clusters')
    plt.title('Number of Clusters for Different Eps Values')
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(eps_values, n_outliers_values, marker='o', linestyle='-')
    plt.xlabel('Eps Value')
    plt.ylabel('Number of Outliers')
    plt.title('Number of Outliers for Different Eps Values')
    plt.grid(True)

    plt.tight_layout()
    plt.show()


def draw_clusters(data, cluster_labels, is_anomaly):
    # Применяем PCA для уменьшения размерности до двух компонент
    pca = PCA(n_components=2)
    data_2d = pca.fit_transform(data)

    # Отображаем точки кластеров на графике
    plt.figure(figsize=(8, 5))
    plt.scatter(data_2d[:, 0], data_2d[:, 1], c=cluster_labels, cmap='plasma', label='Clusters')

    # Отображаем аномальные точки на графике
    plt.scatter(data_2d[is_anomaly][:, 0], data_2d[is_anomaly][:, 1], c='red', marker='x', label='Anomalies') 

    plt.legend()
    plt.show()


def count_points_in_clusters(cluster_labels):
    # Используем словарь для подсчета количества точек в каждом кластере
    cluster_counts = {}
    for label in set(cluster_labels):
        # if label == -1:
        #     continue  # Пропустить выбросы
        cluster_counts[label] = np.sum(cluster_labels == label)

    # Выводим количество точек в каждом кластере
    for label, count in cluster_counts.items():
        print(f"Кластер {label}: {count} точек")

def analyze_clusters(data, cluster_labels, all_technologies):
    # Создаем DataFrame из исходных данных
    df = pd.DataFrame(data=data, columns=all_technologies)
    
    # Определим уникальные метки кластеров
    unique_clusters = np.unique(cluster_labels)
    
    for cluster_index in unique_clusters:
        # if cluster_index == -1:
        #     continue  # Пропустить выбросы
        # Индексы точек, принадлежащих кластеру cluster_index
        cluster_indices = np.where(cluster_labels == cluster_index)[0]
        
        # Создаем DataFrame для данных в текущем кластере
        cluster_df = df.iloc[cluster_indices]
        
        # Вычисляем максимальные значения по каждой колонке (по столбцам)
        max_values = cluster_df.max()

        mean_values = cluster_df.mean(axis=1)  # среднее mean_values
        max_sums = cluster_df.max(axis=1) # максимальные суммы max_sums

        
        # Получаем индексы 10 наибольших максимальных значений
        top_10_indices = max_values.argsort()[-5:]
        
        # Извлекаем названия колонок, соответствующие этим индексам
        top_10_columns = cluster_df.columns[top_10_indices]
        
        # Выводим информацию о кластере и его топ-10 колонках
        print(f"Кластер {cluster_index}:")
        print(f"Топ-10 колонок с наибольшими максимальными значениями:")
        print(top_10_columns)
        print()

def draw_heat_map(data, columns_names, cluster_labels, n_top=10):
    # Создать DataFrame из данных с метками кластеров
    clustered_data = pd.DataFrame(data, columns=columns_names)
    clustered_data['Cluster'] = cluster_labels

    # clustered_data - это DataFrame с данными, 'Cluster' - это название колонки с метками кластеров

    # Подсчитать количество элементов в каждом кластере
    cluster_counts = clustered_data['Cluster'].value_counts()

    # Отфильтровать только кластеры, в которых количество элементов больше или равно 5
    valid_clusters = cluster_counts[cluster_counts >= 1].index

    # Создать новый DataFrame только с данными из выбранных кластеров
    filtered_clustered_data = clustered_data[clustered_data['Cluster'].isin(valid_clusters)]


    # Вычислить средние значения для каждого кластера - медиана
    cluster_means = filtered_clustered_data.groupby('Cluster').median() # mean()  # sum()  # median() 

    # Выбрать топ-10 технологий с наибольшими средними значениями
    top_10_technologies = cluster_means.max().sort_values(ascending=False).index[:n_top]

    # Отфильтровать данные по выбранным топ-10 технологиям
    cluster_means_filtered = cluster_means[top_10_technologies]

    # Создать тепловую карту различий
    plt.figure(figsize=(10, 10))
    sns.heatmap(cluster_means_filtered.T, annot=True, cmap='YlGnBu', fmt='.2f')
    plt.title('Различия между кластерами (топ технологий)')
    plt.show()

def draw_heat_map_sum(data, columns_names, cluster_labels):
    # Создать DataFrame из данных с метками кластеров
    clustered_data = pd.DataFrame(data, columns=columns_names)
    clustered_data['Cluster'] = cluster_labels

    # clustered_data - это DataFrame с данными, 'Cluster' - это название колонки с метками кластеров

    # Подсчитать количество элементов в каждом кластере
    cluster_counts = clustered_data['Cluster'].value_counts()

    # Отфильтровать только кластеры, в которых количество элементов больше или равно 5
    valid_clusters = cluster_counts[cluster_counts >= 5].index

    # Создать новый DataFrame только с данными из выбранных кластеров
    filtered_clustered_data = clustered_data[clustered_data['Cluster'].isin(valid_clusters)]


    # Вычислить средние значения для каждого кластера - медиана
    cluster_means = filtered_clustered_data.groupby('Cluster').sum() # mean()  # sum()  # median() 

    # Выбрать топ-10 технологий с наибольшими средними значениями
    top_10_technologies = cluster_means.max().sort_values(ascending=False).index[:10]

    # Отфильтровать данные по выбранным топ-10 технологиям
    cluster_means_filtered = cluster_means[top_10_technologies]

    # Создать тепловую карту различий
    plt.figure(figsize=(10, 10))
    sns.heatmap(cluster_means_filtered.T, annot=True, cmap='YlGnBu', fmt='.2f')
    plt.title('Различия между кластерами (топ-10 технологий)')
    plt.show()



def look_at_anomalies():
    return 


