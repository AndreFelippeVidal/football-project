import streamlit as st
import pandas as pd
import altair as alt

from utils.database import get_connection

def team_summary():

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
    st.markdown('<div class="center-title">Teams Summary</div>', unsafe_allow_html=True)

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

    st.header(f"{selected_team}")
    
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
        st.subheader("Squad")
        st.dataframe(df_team_players,
                     use_container_width=True,
                     hide_index=True,
                     column_config={
                                "player_name": "Player Name",
                                "player_position": "Player Position",
                                "player_nationality":  "Player Nationality",
                                "player_date_of_birth": "Player Date of Birth",
                    }
        )
    with df_col2:
        st.subheader("Running Competitions")
        st.dataframe(df_team_running_competitions,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                            "competition_emblem": st.column_config.ImageColumn(
                                "Competition Emblem"
                            ),
                            "competition_name": "Competition Name",
                            "competition_type": "Competition Type"
                    },
        )

    try:
        conn = get_connection()
        ## removing cups from the query
        query = f"""select season, position 
                       from staging.stg_fb__competitions_standings sfcs 
                    where team_id = {team_id} and competition_id not in (2000,2001,2018,2152) 
                    order by season"""
        df_seasons_position = pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Erro ao conectar no PostgreSQL: {e}")

    df_seasons_position['season'] = df_seasons_position['season'].astype(str)

    # Adicionar uma coluna para indicar se o time melhorou ou piorou
    df_seasons_position['change'] = df_seasons_position['position'].diff()

    # Calcular se o time melhorou ou piorou com base na última mudança
    # Se a mudança for negativa (melhorou), a cor será verde, senão será vermelha
    change_color = 'green' if df_seasons_position['change'].iloc[-1] < 0 else ('red' if df_seasons_position['change'].iloc[-1] > 0 else 'grey')


    # Calcular os valores mínimo e máximo da posição
    min_position = df_seasons_position['position'].min()
    max_position = df_seasons_position['position'].max()

    # Adicionar um valor a mais para o eixo Y
    y_min = min_position - 2
    y_max = max_position + 2

    # Criar o gráfico de linhas
    line_chart = (
        alt.Chart(df_seasons_position)
        .mark_line(point=True, size=3, color=change_color)  # Adiciona pontos aos vértices
        .encode(
            x=alt.X("season:N", title="Season",axis=alt.Axis(labelAngle=45)),  # Eixo X (Ordinal)
            y=alt.Y("position:Q", scale=alt.Scale(reverse=True, domain=[y_min, y_max], nice=True), title="Position"),
            tooltip=["season", "position"]  # Tooltip ao passar o mouse
        )
        .configure_axis(
            # domain=False,  # Remover o domínio do gráfico

        )
        .properties(
            width=600,  # Largura do gráfico
            height=400,  # Altura do gráfico
            title="Team Position Evolution"
        )
    )

    st.subheader("Statistics")
    # Mostrar o gráfico no Streamlit
    st.altair_chart(line_chart, use_container_width=True)

team_summary()