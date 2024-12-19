import streamlit as st
import pandas as pd
import plotly.express as px

from utils.gpt_prompt import generate_gpt_prompt, get_gpt_report
from utils.database import get_connection

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


data_quality_summary()