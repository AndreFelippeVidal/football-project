import os
import streamlit as st
import pandas as pd
import psycopg2
import altair as alt
import plotly.express as px
from utils.gpt_prompt import generate_gpt_prompt, get_gpt_report

st.set_page_config(page_title='Football Project', layout='wide')

# Função para conectar ao banco PostgreSQL no Render
def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("PG_DB"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASS"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT")
    )

def competitions_summary():

    st.markdown(
        """
        <style>
        .center-title {
            text-align: center;
            font-size: 2.5em; /* Tamanho opcional */
            font-weight: bold; /* Opcional para deixar em negrito */
            color: white; /* Cor do texto */
        }
        </style>
        """,
        unsafe_allow_html=True,
)

    # Título centralizado
    st.markdown('<div class="center-title">Competitions Summary</div>', unsafe_allow_html=True)

    try:
        conn = get_connection()
        query = """select position, team_crest, team_tla, team_short_name, points,
                          played_games, won, draw, lost, goals_for, goals_against, goal_difference,
                          c.competition_name, c.emblem, c.area->>'name' as area_name, c.area->>'flag' as area_flag, season, s.competition_id
                        from staging.stg_fb__competitions_standings s inner join staging.stg_fb__competitions c 
                      on s.competition_id = c.competition_id;"""
        df_competitions = pd.read_sql(query, conn)

        query = """select team_crest, player_name, player_section, player_nationality, player_date_of_birth,
                          goals, assists, penalties, played_matches,
                          c.competition_name, season, ts.competition_id
                        from staging.stg_fb__competitions_top_scorers ts inner join staging.stg_fb__competitions c 
                      on ts.competition_id = c.competition_id;"""
        df_top_scorers = pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Erro ao conectar no PostgreSQL: {e}")

    st.sidebar.header("Filters")

    # Dropdown de competição
    selected_competition = st.sidebar.selectbox("Selecione a Competição", 
                                                options=df_competitions["competition_name"].unique(), 
                                                key="competition")
    
    # Filtrar dados pela competição selecionada
    filtered_competition = df_competitions[df_competitions["competition_name"] == selected_competition]
    filtered_top_scorers = df_top_scorers[df_top_scorers["competition_name"] == selected_competition]

    seasons = filtered_competition["season"].unique()

    df_col1, df_col2 = st.columns(2)

    with df_col1:
        st.header(filtered_competition["area_name"].iloc[0] + " - " + filtered_competition["competition_name"].iloc[0])

    with df_col2:
        if filtered_competition["area_flag"].unique():
            st.markdown(
            f"""
            <div style="text-align: right;">
                <img src="{filtered_competition["area_flag"].iloc[0]}" alt="Competition" width="80">
            </div>
            """,
            unsafe_allow_html=True
            )

    sorted_season = sorted(seasons, reverse=True)
    tabs = st.tabs([str(season) for season in sorted_season])

    for i, season in enumerate(sorted_season):
        with tabs[i]:
            season_data = filtered_competition[filtered_competition["season"] == season]
            st.dataframe(season_data.drop(["competition_name", "season", 
                                           "competition_id", "area_name", "emblem", "area_flag"],axis=1),
                         use_container_width=True,
                         hide_index=True,
                         column_config={
                                "team_tla": "TLA",
                                "team_short_name": "Team",
                                "team_crest":  st.column_config.ImageColumn(
                                    "Flag"
                                ),
                                "form": "Form",
                                "status": "Status",
                                "position": "Position",
                                "points": "Points",
                                "played_games": "Played Games",
                                "won": "Won",
                                "draw": "Draw",
                                "lost": "Lost",
                                "goals_for": "Goals For",
                                "goals_against": "Goals Against",
                                "goal_difference": "Goals Difference",
                        },
                )
            top_scorers_data = filtered_top_scorers[filtered_top_scorers["season"] == season]

            st.header(f"Top Scorers for Season {season}")
            st.dataframe(top_scorers_data.drop(["competition_name", "season", "competition_id",
                                                "player_section", "player_date_of_birth"], axis=1),
                         use_container_width=True,
                         hide_index=True,
                         column_config={
                                "team_short_name": "Team",
                                "player_name": "Player Name",
                                "player_nationality": "Player Nationality",
                                "played_matches": "Played Matches",
                                "goals": "Goals",
                                "assists": "Assists",
                                "penalties": "Penalties",
                                "team_crest":  st.column_config.ImageColumn(
                                    "Flag"
                                ),
                        }
            )
            
    


def matches_today_summary():
    try:
        conn = get_connection()
        query = """select match_area_flag, match_area_code, competition_name,
                          home_team_crest, home_team_short_name, home_final_score,
                          away_final_score, away_team_short_name, away_team_crest,
                          status, utc_date, date_from
                      from staging.stg_fb__matches_today ;"""
        df_matches_today = pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Erro ao conectar no PostgreSQL: {e}")

    st.markdown(
        """
        <style>
        .center-title {
            text-align: center;
            font-size: 2.5em; /* Tamanho opcional */
            font-weight: bold; /* Opcional para deixar em negrito */
            color: white; /* Cor do texto */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Título centralizado
    st.markdown('<div class="center-title">Matches Today</div>', unsafe_allow_html=True)

    st.dataframe(df_matches_today.drop('date_from', axis=1),
                 use_container_width=True,
                 hide_index=True,
                 column_config={
                        "match_area_flag": st.column_config.ImageColumn(
                            "Area"
                        ),
                        "match_area_code": "Code",
                        "competition_name": "Competition Name",
                        "home_team_short_name": "Home",
                        "away_team_short_name": "Away",
                        "home_team_crest":  st.column_config.ImageColumn(
                            "Home Flag"
                        ),
                        "away_team_crest":  st.column_config.ImageColumn(
                            "Away Flag"
                        ),
                        "status": "Status",
                        "home_final_score": "Home Score",
                        "away_final_score": "Away Score",
                        "utc_date": st.column_config.DatetimeColumn(
                            "Schedule",
                            format="D MMM YYYY, h:mm a",
                        ),

                 },
        )

def data_quality_summary():
    def get_columns(table_name):
        """
        Retorna os nomes das colunas para uma tabela específica no schema 'raw'.
        """
        conn = get_connection()
        query = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'raw' AND table_name = '{table_name.split('.')[1]}';
        """
        with conn.cursor() as cur:
            cur.execute(query)
            columns = [row[0] for row in cur.fetchall()]
        conn.close()
        return columns

    def get_null_percentage(table_name, columns):
        """
        Retorna a porcentagem de nulos para cada coluna da tabela fornecida.
        """
        conn = get_connection()
        # Gerando a parte da query para contar os nulos por coluna
        column_checks = ", ".join([f"COUNT(CASE WHEN {col} IS NULL THEN 1 END) AS {col}_nulls" for col in columns])
        query = f"""
            SELECT COUNT(*) AS total_rows, {column_checks}
            FROM {table_name};
        """
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()

        conn.close()
        total_rows = result[0]
        null_percentages = {columns[i]: (result[i+1] / total_rows) * 100 for i in range(len(columns))}
        return null_percentages

    def validate_data_quality(table_name):
        """
        Valida a qualidade dos dados para a tabela, calculando a porcentagem de nulos por coluna.
        """
        columns = get_columns(table_name)
        null_percentages = get_null_percentage(table_name, columns)
        
        # Criando o DataFrame para exibição
        df_results = pd.DataFrame(list(null_percentages.items()), columns=["column", "null_percentage"])
        
        return df_results
        
    st.title("Data Quality")
    table_name = st.selectbox("Choose the table name:", 
                                options=["raw.teams","raw.competitions"], 
                                key="raw.teams")

    if table_name:    
        df_results = validate_data_quality(table_name)

        # Filtra as colunas que têm nulos
        df_results_filtered = df_results[df_results["null_percentage"] > 0]

        if df_results_filtered.empty:
            report = """**Data Quality Automated report didn't find any values to report**"""
        else:
            # Null values graph
            st.subheader("Null Values Percentage per Column")
            st.markdown(f"**Columns being evaluated:** {len(df_results)}")
            fig = px.bar(
                df_results_filtered.sort_values(by=["null_percentage", "column"], ascending=[False, True]),
                x="column",
                y="null_percentage",
                title="Null Values Percentage",
                labels={"column": "Column", "null_percentage": "% Nulls"}
            )
            st.plotly_chart(fig)
            st.header("Open AI Report - Data Quality Recommendations")
            prompt = generate_gpt_prompt(df_results_filtered, table_name)
            report = get_gpt_report(prompt)
        st.markdown(report)

def team_summary():
    try:
        conn = get_connection()
        query = """select competition_name, team_id, team_area_flag, team_area_name, team_name,
		                  tla, crest, club_colors, coach_name as coach, coach_contract_end,
                          t.load_timestamp
		              from staging.stg_fb__teams t inner join staging.stg_fb__competitions c 
                      on t.competition_id = c.competition_id;"""
        df_teams = pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Erro ao conectar no PostgreSQL: {e}")

    
    st.sidebar.header("Filters")
    
    # Dropdown de competição
    selected_competition = st.sidebar.selectbox("Selecione a Competição", 
                                                options=df_teams["competition_name"].unique(), 
                                                key="competition")
    
    # Filtrar times pela competição selecionada
    filtered_teams = df_teams[df_teams["competition_name"] == selected_competition]

    # Dropdown de time (dependente da competição)
    selected_team = st.sidebar.selectbox("Selecione o Time", 
                                         options=filtered_teams["team_name"].unique(), 
                                         key="team")
    
    # Filtrar informações do time selecionado
    team_info = filtered_teams[filtered_teams["team_name"] == selected_team].iloc[0]
    team_id = team_info["team_id"]

    try:
        conn = get_connection()
        query = f"""select player_name, player_position, player_nationality, player_date_of_birth
                      from staging.stg_fb__players where team_id = {team_id}
                    order by 1"""
        df_team_players = pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Erro ao conectar no PostgreSQL: {e}")

    try:
        conn = get_connection()
        query = f"""select competition_name, competition_type, competition_emblem
                      from staging.stg_fb__running_competitions where team_id = {team_id}
                    order by 1"""
        df_team_running_competitions = pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Erro ao conectar no PostgreSQL: {e}")

    st.title(f"Team: {selected_team}")
    
    # Separar informações em colunas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.image(team_info["crest"], caption=team_info["team_name"], width=150)

    with col2:
        st.write(f"**Team ID:** {team_info['team_id']}")
        st.write(f"**TLA:** {team_info['tla']}")
        st.write(f"**Club Colors:** {team_info['club_colors']}")
        st.write(f"**Coach:** {team_info['coach']}")
        st.write(f"**Coach Contract End:** {team_info['coach_contract_end']}")

    with col3:
        st.write(f"**Area:** {team_info['team_area_name']}")
        st.write(f"**Competition:** {team_info['competition_name']}")
        st.write(f"**Last Ingestion:** {team_info['load_timestamp']}")

    with col4:
        if team_info["team_area_flag"]:
            st.markdown(
            f"""
            <div style="text-align: right;">
                <img src="{team_info["team_area_flag"]}" alt="Competition" width="80">
            </div>
            """,
            unsafe_allow_html=True
            )
    
    df_col1, df_col2 = st.columns(2)
    with df_col1:
        st.dataframe(df_team_players,use_container_width=True,hide_index=True)
    with df_col2:
        st.dataframe(df_team_running_competitions,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                            "competition_emblem": st.column_config.ImageColumn(
                                "Competition Emblem"
                            )
                    },
        )


# Função principal para controle da navegação
def main():
    # Sidebar para escolher a página
    page = st.sidebar.selectbox('Choose the page:', ['Matches Today','Teams Summary', 'Competitions Summary', 'Data Quality'])

    if page == 'Teams Summary':
        team_summary()
    elif page == 'Data Quality':
        data_quality_summary()
    elif page == 'Matches Today':
        matches_today_summary()
    elif page == 'Competitions Summary':
        competitions_summary()

# Executar a aplicação
if __name__ == '__main__':
    main()


# try:
#     conn = get_connection()
#     query = "SELECT * FROM marts.mart_fbs__competitions LIMIT 20"
#     df = pd.read_sql(query, conn)
# except Exception as e:
#     st.error(f"Erro ao conectar no PostgreSQL: {e}")


# # Título da aplicação
# st.title("Análise de Competições")

# # Exibição do gráfico
# st.subheader("Gráfico de Agregações")
# chart = (
#     alt.Chart(df)
#     .mark_bar()
#     .encode(
#         x=alt.X("competition_name:N", sort="-y", title="Competição"),  # Competição no eixo X
#         y=alt.Y("teams_count:Q", title="Número de Times"),  # Número de times no eixo Y
#         color=alt.Color("competition_name:N", legend=None),  # Cores por competição
#         tooltip=["competition_name", "teams_count"],  # Tooltip para exibição interativa
#     )
#     .properties(width=700, height=400, title="Número de Times por Competição")
# )

# st.altair_chart(chart, use_container_width=True)

# # Seção expandível para o DataFrame
# with st.expander("Ver Dados em Tabela"):
#     st.subheader("Tabela de Dados")
#     st.dataframe(df)