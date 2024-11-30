import os
import streamlit as st
import pandas as pd
import psycopg2
import altair as alt

# Função para conectar ao banco PostgreSQL no Render
def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("PG_DB"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASS"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT")
    )

try:
    conn = get_connection()
    query = "SELECT * FROM marts.mart_fbs__competitions LIMIT 20"
    df = pd.read_sql(query, conn)
except Exception as e:
    st.error(f"Erro ao conectar no PostgreSQL: {e}")


# Título da aplicação
st.title("Análise de Competições")

# Exibição do gráfico
st.subheader("Gráfico de Agregações")
chart = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        x=alt.X("competition_name:N", sort="-y", title="Competição"),  # Competição no eixo X
        y=alt.Y("teams_count:Q", title="Número de Times"),  # Número de times no eixo Y
        color=alt.Color("competition_name:N", legend=None),  # Cores por competição
        tooltip=["competition_name", "teams_count"],  # Tooltip para exibição interativa
    )
    .properties(width=700, height=400, title="Número de Times por Competição")
)

st.altair_chart(chart, use_container_width=True)

# Seção expandível para o DataFrame
with st.expander("Ver Dados em Tabela"):
    st.subheader("Tabela de Dados")
    st.dataframe(df)