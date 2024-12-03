from datetime import datetime, timedelta

from airflow.models.dag import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

create_table_query= '''
    CREATE TABLE IF NOT EXISTS animal_adoptions_combined (
        date DATE,
        type VARCHAR,
        name VARCHAR,
        age INTEGER
        );
'''

combine_data_query= '''
    INSERT INTO animal_adoptions_combined (date, type, name, age) 
        SELECT * 
        FROM adoption_center_1
        UNION 
        SELECT *
        FROM adoption_center_2;
'''

with DAG(
    'lineage-combine-postgres',
    start_date=datetime(2022, 12, 1),
    max_active_runs=1,
    schedule='@daily',
    default_args = {
        'retries': 1,
        'retry_delay': timedelta(minutes=1)
    },
    catchup=False
):

    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='postgres_default',
        sql=create_table_query
    ) 

    insert_data = PostgresOperator(
        task_id='combine',
        postgres_conn_id='postgres_default',
        sql=combine_data_query
    ) 

    create_table >> insert_data