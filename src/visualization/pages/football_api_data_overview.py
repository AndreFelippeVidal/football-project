import streamlit as st
import pandas as pd
import altair as alt

from utils.database import get_connection

try:
    conn = get_connection()
    query = "SELECT * FROM marts.mart_fbs__competitions LIMIT 20"
    df = pd.read_sql(query, conn)
except Exception as e:
    st.error(f"Error to connect to PostgreSQL: {e}")


# Título da aplicação
st.title("Competitions Data")

# Exibição do gráfico
chart = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        x=alt.X("competition_name:N", sort="-y", title="Competition"),  # Competição no eixo X
        y=alt.Y("teams_count:Q", title="Number of teams"),  # Número de times no eixo Y
        color=alt.Color("competition_name:N", legend=None),  # Cores por competição
        tooltip=["competition_name", "teams_count"],  # Tooltip para exibição interativa
    )
    .properties(width=700, height=400, title="Number of teams by available competitions")
)

st.altair_chart(chart, use_container_width=True)

# Seção expandível para o DataFrame
with st.expander("Tabular Data"):
    st.dataframe(df, hide_index=True)