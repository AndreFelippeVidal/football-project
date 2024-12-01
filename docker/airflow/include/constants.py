"Contains constants used in the DAGs"

from pathlib import Path
from cosmos import ExecutionConfig

football = Path("/usr/local/airflow/dbt/dbt_football")
dbt_executable = Path("/usr/local/airflow/dbt_venv/bin/dbt")

venv_execution_config = ExecutionConfig(
    dbt_executable_path=str(dbt_executable),
)