import streamlit as st
import pandas as pd

from utils.database import get_connection

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
    
matches_today_summary()