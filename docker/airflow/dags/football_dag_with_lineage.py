from airflow.decorators import dag
from airflow.models import Variable
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from cosmos import DbtTaskGroup, ProjectConfig, RenderConfig
from airflow.lineage.entities import Table, File, Column, User


from include.profiles import render_postgres_db
from include.constants import football, venv_execution_config
from datetime import datetime


environment_vars = {
        "API_KEY": Variable.get("API_KEY"),
        "PG_HOST": Variable.get("PG_HOST"),
        "PG_PASS": Variable.get("PG_PASS"),
        "PG_USER": Variable.get("PG_USER"),
        "PG_PORT": Variable.get("PG_PORT"),
        "PG_DB": Variable.get("PG_DB"),
        "PG_SCHEMA": Variable.get("PG_SCHEMA"),
        "PG_THREADS": Variable.get("PG_THREADS"),
    }

# Definindo as sources manuais pro open lineage para linkar com o dbt
api_competitions = Table(
    cluster="postgres://dpg-ct4ike9u0jms73a8mtf0-a.oregon-postgres.render.com:5432",
    database="football_db_v5as",
    name="raw.competitions",
    extra={'dataSource':'football-org.api'}
)

api_teams = Table(
    cluster="postgres://dpg-ct4ike9u0jms73a8mtf0-a.oregon-postgres.render.com:5432",
    database="football_db_v5as",
    name="raw.teams",
    extra={'dataSource':'football-org.api'}
)

results = Table(
    cluster="postgres://dpg-ct4ike9u0jms73a8mtf0-a.oregon-postgres.render.com:5432",
    database="football_db_v5as",
    name="marts.mart_fbs__competitions",
)

# Defina os argumentos padrão para a DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 11, 28),
    'retries': 0,
}

@dag(
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
    tags=["football-flow"],
    max_active_runs=1
)
def futebol_pipeline_with_lineage() -> None:

    docker_task_competitions = DockerOperator(
        task_id='run_footbal_pipeline_competitions',  # Nome da task
        image='football_image',     # Nome da imagem Docker local
        api_version='auto',
        auto_remove=True,  # Remove o container após a execução
        command='poetry run python /src/main.py --request_type competitions',   # Comando para rodar o código Python no container
        docker_url='unix://var/run/docker.sock',  # Conexão com o Docker local
        network_mode='bridge',            # Definindo o modo de rede do Docker
        #volumes=['/src:/src'],  # Montando o diretório local para o container
        environment=environment_vars,
        outlets=[api_competitions]
    )

    # Defina a task DockerOperator
    docker_task_teams = DockerOperator(
        task_id='run_football_pipeline_teams',  # Nome da task
        image='football_image',     # Nome da imagem Docker local
        api_version='auto',
        auto_remove=True,  # Remove o container após a execução
        command='poetry run python /src/main.py --request_type teams',   # Comando para rodar o código Python no container
        docker_url='unix://var/run/docker.sock',  # Conexão com o Docker local
        network_mode='bridge',            # Definindo o modo de rede do Docker
        #volumes=['/src:/src'],  # Montando o diretório local para o container
        environment=environment_vars,
        outlets=[api_teams]
    )
    
    dbt_transformations = DbtTaskGroup(
        group_id="dbt_football_project",
        project_config=ProjectConfig(football),
        profile_config=render_postgres_db,
        execution_config=venv_execution_config,
        render_config=RenderConfig(
            exclude=["path:models/marts"],
        ), # Exclui os testes da execução inicial
    )

    dbt_marts = DbtTaskGroup(
        group_id="dbt_football_marts",
        project_config=ProjectConfig(football),
        profile_config=render_postgres_db,
        execution_config=venv_execution_config,
        render_config=RenderConfig(
            select=["path:models/marts"],
        ),  # Executa apenas os testes
    )

    query_table = PostgresOperator(
            task_id="query_table",
            postgres_conn_id="render_postgres_connection",
            sql=f"SELECT * FROM marts.mart_fbs__competitions",
        )


    docker_task_competitions >> docker_task_teams 
    docker_task_teams >> dbt_transformations >> dbt_marts >> query_table
    

futebol_pipeline_with_lineage()