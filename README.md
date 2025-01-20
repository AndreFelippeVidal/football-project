# FOOTBALL PROJECT

---

## Project Description

This project serves as a portfolio to demonstrate data engineering skills, covering the complete data lifecycle: **extraction, ingestion, transformation, orchestration, storage, visualization, and governance**. It leverages modern technologies and industry best practices, including **Docker**, **Airflow**, **Python** with **Poetry**, **PostgreSQL**, **dbt**, **Streamlit**, **MinIO (not yet)**, **MkDocs**, **Logfire**, and **OpenLineage**.

Note: Focused on prototyping various tools to understand their usage, not on building the best and fastest processes.

---

## General Workflow

1. **Data Ingestion**:  
   Fetch data from a public football API and store it in a PostgreSQL database. [API Extraction Docs](githubpages)

2. **Data Transformation**:  
   Process the data using **Python** and **dbt** to organize the Data Warehouse layers (staging, intermediate, mart).

3. **Orchestration**:  
   Use **Airflow** to manage the data pipeline. Airflow will invoke **custom Docker images** to process the data.  
   Note: We use the Astronomer version for simplicity; download it to streamline the process.  
   Note2: In the airflow settings file configured by Astronomer, include your API key and PostgreSQL settings in the `airflow_settings.yaml` file:  
   ```yaml
   variables:
    - variable_name: API_KEY
      variable_value: <YOUR API KEY>
   ```
   A sample fale was added: `sample_airflow_settings.yml`
   Info: I've Changed Astro PostgreSQL port: `astro config set postgres.port 5435`
   There is also an `sample.env` that needs to be configured with the token for logfire.

4. **Governance and Quality**:  
   - Open Metadata as a data catalog and data governance tool, with the aditional data quality integrations. (Not ready)
   - For Data Quality apply data contracts with pydantic.

5. **Visualization and Reporting**:  
   Create interactive dashboards with **Streamlit** and export reports to **MinIO**.

6. **Documentation**:  
   Use **MkDocs** with the **Material for MkDocs** theme to document the project, including technical details, architecture, and usage instructions.

7. **Observability**:  
   Use **Logfire** as an observability tool to monitor the environment.

---

## Technologies Used

- **Orchestration**: Apache Airflow  
- **Processing**: Python (with Poetry, Pydantic)  
- **Transformation**: dbt (Data Build Tool)  
- **Database**: PostgreSQL  
- **Visualization**: Streamlit  
- **Report Storage**: MinIO (S3 simulation)
- **Containerization**: Docker and Docker Compose  
- **Data Validation**: TBD  
- **Data Lineage**: OpenLineage integrated with Airflow  
- **Documentation**: MkDocs (Material for MkDocs)  
- **Observability**: Logfire

---

## How to Run

### Pre-requisites
1. Docker
2. Python `3.12.15`
3. Poetry
4. Astro CLI
5. Postgres Database - I choose to create one using Render for **Free** that would be easier to connect and to handle.
6. [Logfire Account](https://logfire.pydantic.dev/login)

### Running Steps (Mac Os)
**Note:** before anything else, update all `.env` files.
   a. on root folder `./`
   b. on airflow folder `docker/airflow/` (`.env` and `airflow_settings.yaml`)


#### Starting the Environment
Open terminal on the root folder of the project and type:
1. `poetry shell && poetry install` - To open the poetry virtual env and install all library dependencies
2. `task build_docker_images` - To generate the python code images
3. `task start airflow` - To start airflow
   a. `task restart_airflow` - To restart airflow if needed
   b. `task stop_airflow` - To stop airflow if needed
4. `task run_marquez` - This can be run in a different terminal window because it will keep running. It will start the marquez server to track the lineage for DataOps reasons.

Once the entire environment is up you can access using the browser:
1. Airflow: [Airflow UI](localhost:8080) - Monitoring and running the orchestration
2. Marquez: [Marquez UI](localhost:3000) - Monitoring the data lineage
3. Logfire: [Logfire UI](https://logfire.pydantic.dev/login) - Monitoring the pipeline healthy

Starting the process:
1. In airflow UI you need to turn the dag into active mode and this will automatically trigger the entire end-to-end process. DAG: `football_pipeline_with_lineage`

Once it end successfully, you can use streamlit to visualize the data.
On Terminal, root folder:
1. `task run_streamlit` - To generate the server
2. Navigate to [Streamlit UI](localhost:8501)

### Useful Info
1. To export the .env variables to your local poetry env and do local testing - On terminal:
```bash
export $(cat .env | xargs)
```  
This is useful for DBT checks.
2. To check project python code documentation locally:
First on terminal:
```bash
mkdocs serve
```  
then [MkDocs UI](http://127.0.0.1:8000/)

---


## Estrutura de Diretórios

```plaintext
project/                   
├── docker/                   # Dockerfiles for different components
│   ├── airflow/              # Airflow Configs
│   │   ├── dags/             # Airflow DAGs
│   │   ├── dbt/              # DBT folder
|   │   │   ├── dbt_football/ # DBT configs and models
│   ├── streamlit/            # Dockerfile do streamlit
│   ├── python/               # Python code Dockerfile 
│   ├── marquez/              # Marquez Dockerfiles
├── docs/                     # Documentation Files (MkDocs)
├── src/                      # Python Source Code
│   ├── contracts/            # Data Contracts
│   ├── utils/                # Python utilities and libraries
│   ├── visualization/        # Streamlit Code
│   ├── main.py               # Python main code
├── tests/                    # Automated tests (pytest)
├── .env                      # Environment Variables
├── pytest.ini                # Minor Pytest configurations
├── mkdocs.yml                # MKdocs Config
├── README.md                 # Readme File
├── poetry.lock               # Poetry lock
└── pyproject.toml            # Poetry Config

```

## Known Issues:
1. There are issues with group stage competitions that needs further investigation.
2. See all upcoming matches for Real Madrid: -- API blocked the access at this endpoint. To be further investigated.
https://api.football-data.org/v4/teams/86/matches?status=SCHEDULED

## Next Steps
0. Refactor README and document python code with docstrings and mkdocs.
1. Implement data catalog with Open Metadata:
   a. Lineage can be added there and marquez can be removed.
   b. Some Data Quality can be implemented in a centralized place with Open Metadata.
2. Integrate airflow with Minio to export reports to an like S3 bucket.
3. Fix known issues with the cup competitions that have group stages and affect the process and the visualization. Known Issue #1
4. Investigate known issue #2.
5. Add more gen AI features
   a. Create tab In Streamlit App with OpenAI to answer questions regarding the data.
