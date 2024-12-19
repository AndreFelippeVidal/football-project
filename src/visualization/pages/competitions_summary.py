import streamlit as st
import pandas as pd

from utils.database import get_connection

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
                          played_games, won, draw, lost, goals_for, goals_against, goal_difference, form,
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
                                "form": st.column_config.ListColumn(
                                    "Recent Form",
                                    help="The form in the last 5 matches",
                                    width="medium",
                                ),
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

competitions_summary()