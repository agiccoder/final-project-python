import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium as fl
from sqlalchemy import create_engine
from streamlit_folium import folium_static

with st.echo(code_location='below'):

    engine = create_engine('sqlite:///english_football.db')

    def get_clubs_location(sql_engine):
        return pd.read_sql("SELECT [Club Name], Latitude, Longitude, City, Stadium, Capacity FROM team", sql_engine)

    def get_all_data(sql_engine):
        return pd.read_sql("SELECT * FROM team", sql_engine)

    def get_goals(sql_engine):
        return pd.read_sql("SELECT [Club Name], [Goals For], Points FROM team", sql_engine)

    def get_games_statuses(sql_engine):
        return pd.read_sql("SELECT [Club Name], Wins, Loses, Draws FROM team", sql_engine)

    def get_dataframe_for_regression(sql_engine, x, y):
        return pd.read_sql("SELECT [{}], [{}] FROM team".format(x, y), sql_engine)

    def create_map(sql_engine):
        location_df = get_clubs_location(sql_engine)
        location_map = fl.Map(location=[location_df.Latitude.mean(), location_df.Longitude.mean()], zoom_start=7,
                              control_scale=True)
        for index, location_info in location_df.iterrows():
            iframe = fl.IFrame(
                'City: ' + location_info["City"] + '<br>' + 'Team Name: ' + location_info[
                    "Club Name"] + '<br>' + 'Home Stadium: ' + location_info["Stadium"] + '<br>' + 'Capacity: ' + str(
                    location_info["Capacity"])
            )
            popup = fl.Popup(iframe, min_width=220, max_width=300)
            fl.Marker([location_info["Latitude"], location_info["Longitude"]], popup=popup).add_to(location_map)
        return location_map

    def create_plot_with_goals(sql_engine, selected_goals):
        goals_df = get_goals(sql_engine)
        sorted_df = goals_df.sort_values(by=['Goals For'])
        filtered_df = sorted_df.loc[sorted_df['Goals For'] < selected_goals]
        fig, ax = plt.subplots(1, 1, figsize=(5, 5))
        plot = sns.scatterplot(data=filtered_df, x="Goals For", y="Points", hue='Club Name', size='Points', ax=ax,
                               edgecolor="black")
        plot.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        return fig

    # def create_plot_with_games_statuses(sql_engine):
    #     statuses_df = get_games_statuses(sql_engine)
    #     statuses_df = statuses_df.sort_values(by=['Wins'])
    #     sns.set_theme(style="ticks")
    #     fig, ax = plt.subplots(figsize=(7, 5))
    #     sns.despine(fig)
    #
    #     sns.barplot(
    #         statuses_df,
    #         x="Club Name", y="Wins"
    #     )
    #     return fig

    def create_regression(sql_engine, x_type, y_type):
        regression_df = get_dataframe_for_regression(sql_engine, x_type, y_type)
        sns.set_theme(style="darkgrid")

        g = sns.jointplot(x=x_type, y=y_type, data=regression_df,
                          kind="reg", truncate=False,
                          color="m", height=7)
        return g

    def find_Pearson_correlation_coefficient(x,y):
        k = np.vstack((x,y))
        r_xy = np.corrcoef(k)
        df_r_xy = pd.DataFrame(r_xy)
        return df_r_xy

    st.title("Описание проекта")
    st.write('В данном проекте я провел исследование прошедшего футбольного сезона Английской Премьер Лиги. '
             'В первой части проекта, которую вы можете найти на github, были получены данные по сезону. '
             'При выполнении первой части использовались продвинутые возможности pandas, Selenium, SQL, REST API, '
             'регулярные выражения. В этой части проекта мы проанализируем некоторые данные, полученные в ходе '
             'предыдущей части. При этом используем folium(геоданные), весьма нетривиальные визуализации с помощью '
             'seaborn, numpy (в ходе получения регрессионной матрицы), а также регресии.')
    st.title('Cities Map')
    st.write('Для начала взглянем на распределение команд, участвовавших в чемпионате, по городам. Здесь представлены '
             'домашние стадионы наших команд.')
    folium_static(create_map(engine))

    df = get_all_data(engine)
    print(df)
    st.title('Выберите количество забитых голов')
    st.write('Здесь представлен график в осях забитые мячи - набранные очки, на котором представлены все команды, '
             'забившие меньше голов, чем выбранное вами число.')
    goals_scored = st.slider('Goals scored', min_value=30, max_value=100)
    st.pyplot(create_plot_with_goals(engine, goals_scored))

    st.title('Линейная регрессия')
    st.write('Здесь вы можете выбрать переменные, по котором будет строиться регрессия. Вы получите график регрессии, '
             'а также матрицу корреляций для выбранных вами переменных')
    regression_x_type = st.selectbox("Select x type",
                                     ["Goals For", "Attendance", "Expected Goals", "Goals Against", "Wins", "Loses",
                                      "Points", "Founded"])
    regression_y_type = st.selectbox("Select y type",
                                     ["Attendance", "Goals For", "Expected Goals", "Goals Against", "Wins", "Loses",
                                      "Points", "Founded"])
    st.pyplot(create_regression(engine, regression_x_type, regression_y_type))
    st.write(find_Pearson_correlation_coefficient(df[regression_x_type], df[regression_y_type]))