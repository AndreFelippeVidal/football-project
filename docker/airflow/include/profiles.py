"Contains profile mappings used in the project"

from cosmos import ProfileConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping


render_postgres_db = ProfileConfig(
    profile_name="render_postgres_db",
    target_name="dev",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id="render_postgres_connection",
        profile_args={"schema": "dbt"},
    ),
)