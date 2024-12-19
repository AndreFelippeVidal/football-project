import streamlit as st

st.set_page_config(page_title='Football Project', layout='wide')

pages = {
    "Competitions": [
        st.Page("pages/matches_today.py", title="Matches Today"),
        st.Page("pages/competitions_summary.py", title="Competitions Summary"),
        st.Page("pages/teams_summary.py", title="Teams Summary"),
    ],
    "Data Quality": [
        st.Page("pages/data_quality.py", title="Data Validation"),
    ],
    "API Summary":[
        st.Page("pages/football_api_data_overview.py", title="API Data Summary"),   
    ]
}

pg = st.navigation(pages)
pg.run()