import os
import streamlit as st
import pandas as pd
import psycopg2
import altair as alt

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
    pagina = st.sidebar.selectbox('Choose the page:', ['Teams Summary', 'Competitions Summary', 'Graphs'])

    if pagina == 'Teams Summary':
        team_summary()
    # elif pagina == 'Dados':
    #     pagina_dados()
    # elif pagina == 'Gráficos':
    #     pagina_grafico()

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