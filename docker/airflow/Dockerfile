FROM quay.io/astronomer/astro-runtime:12.4.0

# install dbt into a virtual environment
RUN python -m venv dbt_venv && source dbt_venv/bin/activate && \
    pip install --no-cache-dir dbt-postgres==1.8.2 && deactivate