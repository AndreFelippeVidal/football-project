from datetime import datetime, timedelta

from airflow.models.dag import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

aggregate_reporting_query = '''
    INSERT INTO adoption_reporting_long (date, type, number)
    SELECT c.date, c.type, COUNT(c.type)
    FROM animal_adoptions_combined c
    GROUP BY date, type;
'''

with DAG(
    'lineage-reporting-postgres',
    start_date=datetime(2020, 6, 1),
    max_active_runs=1,
    schedule='@daily',
    default_args={
        'retries': 1,
        'retry_delay': timedelta(minutes=1)
    },
    catchup=False
):

    create_table = PostgresOperator(
        task_id='create_reporting_table',
        postgres_conn_id='postgres_default',
        sql='''
            CREATE TABLE IF NOT EXISTS adoption_reporting_long (
                date DATE,
                type VARCHAR,
                number INTEGER
                );
        ''',
    ) 

    insert_data = PostgresOperator(
        task_id='reporting',
        postgres_conn_id='postgres_default',
        sql=aggregate_reporting_query
    ) 

    create_table >> insert_data