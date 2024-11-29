from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime
from airflow.models import Variable

environment_vars = {
        "API_KEY": Variable.get("API_KEY"),
    }

# Defina os argumentos padrão para a DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 11, 28),
    'retries': 0,
}

dag = DAG(
    'futebol_pipeline',
    default_args=default_args,
    schedule_interval=None,  # Defina o intervalo de execução
    catchup=False,
    max_active_runs=1,
)

# Defina a task DockerOperator
docker_task_teams = DockerOperator(
    task_id='run_futebol_pipeline_teams',  # Nome da task
    image='football_image',     # Nome da imagem Docker local
    api_version='auto',
    auto_remove=True,  # Remove o container após a execução
    command='poetry run python /src/main.py --request_type teams',   # Comando para rodar o código Python no container
    docker_url='unix://var/run/docker.sock',  # Conexão com o Docker local
    network_mode='bridge',            # Definindo o modo de rede do Docker
    #volumes=['/src:/src'],  # Montando o diretório local para o container
    dag=dag,
    environment=environment_vars,
)

docker_task_competitions = DockerOperator(
    task_id='run_futebol_pipeline_competitions',  # Nome da task
    image='football_image',     # Nome da imagem Docker local
    api_version='auto',
    auto_remove=True,  # Remove o container após a execução
    command='poetry run python /src/main.py --request_type competitions',   # Comando para rodar o código Python no container
    docker_url='unix://var/run/docker.sock',  # Conexão com o Docker local
    network_mode='bridge',            # Definindo o modo de rede do Docker
    #volumes=['/src:/src'],  # Montando o diretório local para o container
    dag=dag,
    environment=environment_vars,
)

docker_task_teams >> docker_task_competitions
