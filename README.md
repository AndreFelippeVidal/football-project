 
# FOOTBALL PROJECT

---

## Descrição do Projeto

Este projeto é um portfólio para demonstrar habilidades como engenheiro de dados, cobrindo o ciclo completo de dados: **ingestão, transformação, orquestração, armazenamento, visualização e governança**. Utilizamos tecnologias modernas e práticas recomendadas da indústria, incluindo **Docker**, **Airflow**, **Python** com **Poetry**, **PostgreSQL**, **dbt**, **Streamlit**, **MinIO**, **MkDocs**, **Great Expectations**, e **OpenLineage**.

---

## Fluxo Geral

1. **Ingestão de Dados**:  
   Obter dados de uma API pública de futebol e armazenar em um banco PostgreSQL.

2. **Transformação de Dados**:  
   Processar os dados com **Python** e utilizar **dbt** para organizar as camadas do Data Warehouse (staging, intermediate, mart).

3. **Orquestração**:  
   Usar o **Airflow** para gerenciar o pipeline de dados. O Airflow chamará **imagens Docker personalizadas** para processar os dados.
   Note: Estaremos utilizando a versao do astronomer. terá de ser baixado para facilitar o processo.
   Note2: no arquivo airflow settings configurado pelo astronomer, inclua sua api_key, e as configurações do postgres, como seu .env
   ```variables:
    - variable_name: API_KEY
      variable_value: <YOUR API KEY>
    ```
    Note: change astro postgres port: `astro config set postgres.port 5435`

4. **Governança e Qualidade**:  
   Validar os dados utilizando **Great Expectations** (ou **Pandera**) para garantir conformidade com o esquema e qualidade.

5. **Visualização e Relatórios**:  
   Criar dashboards interativos com **Streamlit** e exportar relatórios para o **MinIO**.

6. **Documentação**:  
   Usar **MkDocs** com o tema **Material for MkDocs** para documentar o projeto, incluindo detalhes técnicos, arquitetura e instruções de uso.

---

## Tecnologias Utilizadas

- **Orquestração**: Apache Airflow  
- **Processamento**: Python (com Poetry, Pydantic, Pandera)  
- **Transformação**: dbt (Data Build Tool)  
- **Banco de Dados**: PostgreSQL  
- **Visualização**: Streamlit  
- **Armazenamento**: MinIO (simulação de S3)  
- **Containerização**: Docker e Docker Compose  
- **Validação de Dados**: Great Expectations ou Pandera  
- **Linhagem de Dados**: OpenLineage integrado ao Airflow  
- **Documentação**: MkDocs (Material for MkDocs)

---

## Etapas do Desenvolvimento

1. **Configuração Inicial**:
   - Configurar o ambiente local com Docker Compose para gerenciar os serviços (Airflow, MinIO).
   - Criar um servidor postgres (Neste caso hospedamos no render pela simplicidade e ser grátis)
   - Criar um repositório Git para versionar o código e usar GitHub Actions para CI/CD.

2. **Ingestão de Dados**:
   - Criar um DAG no Airflow que se conecta à API de futebol para baixar dados e armazenar em um banco PostgreSQL.
   - Configurar o Airflow para usar o `DockerOperator` e chamar containers Python personalizados.

3. **Transformação de Dados**:
   - Configurar dbt para criar tabelas de staging, camada intermediária e marts no PostgreSQL.
   - Criar queries para calcular métricas como número de gols, desempenho por time, etc.
   Note: Para exportar as variáveis de ambiente para que o dbt consiga utilizar, é necessário utilizar o comando abaixo:
   `export $(cat .env | xargs)`
   ~~Note2: A primeira vez executando o pipeline do zero, é valido rodar um dbt run para criar todas as views/tableas primeiro na tabela final, pois existem relações entre as tabelas que podem falhar no pipeline caso todas não existam ainda. Pode-se executar local antes de subir para rodar via airflow.~~ (Fixed)


4. **Governança e Qualidade**:
   ~~- Usar Great Expectations para validar os dados no pipeline (esquema, tipos de dados, valores duplicados).~~
   - Adicionar contratos de dados com Pydantic para processamentos e qualidade dos dados em Python.
   - Implementar data lineage com open lineage e marquez. Para subir o docker do marquez, navegar até `docker/marquez` e executar: `./docker/up.sh`

5. **Visualização e Relatórios**:
   - Desenvolver um dashboard com Streamlit que exibe métricas calculadas.
   Note: Para executar o streamlit são necessários dois passos:
    1. Criar a imagem estando na raiz do projeto: `docker build -f docker/streamlit/Dockerfile -t streamlit-app .`
    2. Executar a imagem e acessar via `localhost:8501`: `docker run --env-file .env -p 8501:8501 streamlit-app`
   - Criar uma task na DAG no Airflow para exportar relatórios para o MinIO.

6. **Documentação**:
   - Usar MkDocs para documentar:
     - Arquitetura do projeto.
     - Tecnologias utilizadas.
     - Fluxo de dados.
     - Configuração e execução.
   - Adicionar a documentação gerada automaticamente pelo código Python utilizando o `mkdocstrings`.

7. **Containerização**:
    - Adicionar automatção com taskipy para buildar imagens docker: `task build_docker_images`

---

## Estrutura de Diretórios

```plaintext
project/                   
├── dbt_football/            # Configuração e modelos dbt
├── docker/                  # Dockerfiles para diferentes componentes
│   ├── airflow/             # Configuração do Airflow
│   │   ├── dags/            # DAGs do Airflow
│   ├── streamlit/           # Dockerfile do streamlit
│   ├── python/              # Dockerfile do código python
├── docs/                    # Arquivos de documentação (MkDocs)
├── src/                     # Código-fonte Python
│   ├── contracts/           # Contratos de Dados
│   ├── utils/               # Bibliotecas e utilitários de python
│   ├── visualization/       # Código Streamlit
│   ├── main.py              # Python main code
├── tests/                   # Testes automatizados (pytest)
├── .env                     # Environment Variables
├── pytest.ini               # Minor Pytest configurations
├── poetry.lock              # Gerado pelo Poetry
└── pyproject.toml           # Configuração do Poetry

```


### NEXT STEPS

1. ~~Pendente rodar o end-to-end de inserção até o banco no airflow. funcionando local~~
2. ~~feito isso, criar o processo do competitions para o team, com contrato no pydantic até inserção no banco~~
3. ~~ Limpar a main, tem muita coisa, jogar dentro de alguma função.~~
4. ~~partir pro dbt visto que os dados já estão na raw.~~
5. ~~Gerar algo no streamlit  básico para visualização.~~
6. ~~Precisa tirar as variáveis do profiles e utilizar as variáveis de ambiente, testar antes de continuar com qualquer outra coisa~~
7. ~~rodar dbt no airflow com cosmos (rever jornada de dados)~~
8. ~~ Verificar com a ajuda do gpt para integrar o open lineage nessa estrutura do airflow~~
9. ~~Gerar documentação com mkdocs? (the build is failing because the repo is private, once moved to public it will work)~~
10. Buscar mais dados na API pra suportar mais dashboards no streamlit (matches, scores, desempenho na temporada, estisticas de jogadores são algumas ideias, mas tem que buscar essas informações na api, o que temos até agora já está no dashboard.)
~~10.1 -> Adicionar os novos modelos do dbt de players e running comeptitions no airflow e testar (Automaticamente gerado pelo dbt integrado ao cosmos)~~ 
11. Implementar greatExpectations se possível (TBD)
12. Colocar uma aba no streamlit com o openai pra fazer perguntas sobre times e a propria ia responder. (TBD)
~~13. Colocar uma aba no streamlit com o open ai para fazer um monitoramento de data quality de cada tabela e a openai sugerir soluções.~~



Novas requests que podem ser implementadas para analises no dashboard:
Get the league table for Eredivisie:
https://api.football-data.org/v4/competitions/{id}/standings

See best 10 scorers of Italy's top league (scorers subresource defaults to limit=10):
https://api.football-data.org/v4/competitions/SA/scorers


See todays' matches of your subscribed competitions:
https://api.football-data.org/v4/matches

See all upcoming matches for Real Madrid:
https://api.football-data.org/v4/teams/86/matches?status=SCHEDULED