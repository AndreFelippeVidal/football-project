 
# Projeto de Portfólio de Engenharia de Dados - # FOOTBALL PROJECT

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

4. **Governança e Qualidade**:
   ~~- Usar Great Expectations para validar os dados no pipeline (esquema, tipos de dados, valores duplicados).~~
   - Adicionar contratos de dados com Pydantic para processamentos e qualidade dos dados em Python.

5. **Visualização e Relatórios**:
   - Desenvolver um dashboard com Streamlit que exibe métricas calculadas.
   - Criar um DAG no Airflow para exportar relatórios para o MinIO.

6. **Documentação**:
   - Usar MkDocs para documentar:
     - Arquitetura do projeto.
     - Tecnologias utilizadas.
     - Fluxo de dados.
     - Configuração e execução.
   - Adicionar a documentação gerada automaticamente pelo código Python utilizando o `mkdocstrings`.

7. **Containerização**:
    - Para buildar a imagem docker utilize: `docker build -t football_image . `
    - Para testar o comando na imagem docker utilize:  `docker run --env-file .env football_image`

---

## Estrutura de Diretórios

```plaintext
project/                   
├── dbt/                     # Configuração e modelos dbt
├── docker/                  # Dockerfiles para diferentes componentes
│   ├── airflow/             # Configuração do Airflow
│   │   ├── dags/            # DAGs do Airflow
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
├── pyproject.toml           # Configuração do Poetry
└── Dockerfile.file          # Python Image to be used in Airflow

```


### NEXT STEPS

1 - Integrar ao Pipeline do Airflow:

Criar um DAG no Airflow que utilize a classe FootballAPI para buscar dados automaticamente.
Configurar tasks para salvar os dados em um banco PostgreSQL.

2 - Validação e Salvamento de Dados:

Integrar o Great Expectations ou o Pandera para validar os dados antes de armazená-los.
Definir o esquema do banco PostgreSQL e escrever funções de salvamento no banco.
Note: Devido a complexidade do great expectations e a documentação esquisita, vou aguardar pra implementar depois.

3 - Preparar a Documentação:

Adicionar a documentação gerada do Python no MkDocs com o plugin mkdocstrings.

### TESTAR
~~1 - Pendente rodar o end-to-end de inserção até o banco no airflow. funcionando local~~
~~2 - feito isso, criar o processo do competitions para o team, com contrato no pydantic até inserção no banco~~
~~3 - Limpar a main, tem muita coisa, jogar dentro de alguma função.~~
4 - partir pro dbt visto que os dados já estão na raw.
5 - Gerar algo no streamlit  básico para visualização.
5.1 - Verificar com a ajuda do gpt para integrar o open lineage nessa estrutura do airflow
6 - Gerar documentação com mkdocs?
7 - Buscar mais dados na API pra suportar mais dashboards no streamlit
8 - Implementar greatExpectations se possível
9 - Colocar uma aba com o openai pra fazer perguntas sobre times e a propria ia responder.