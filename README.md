 
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
   - Configurar o ambiente local com Docker Compose para gerenciar os serviços (Airflow, PostgreSQL, MinIO).
   - Criar um repositório Git para versionar o código e usar GitHub Actions para CI/CD.

2. **Ingestão de Dados**:
   - Criar um DAG no Airflow que se conecta à API de futebol para baixar dados e armazenar em um banco PostgreSQL.
   - Configurar o Airflow para usar o `DockerOperator` e chamar containers Python personalizados.

3. **Transformação de Dados**:
   - Configurar dbt para criar tabelas de staging, camada intermediária e marts no PostgreSQL.
   - Criar queries para calcular métricas como número de gols, desempenho por time, etc.

4. **Governança e Qualidade**:
   - Usar Great Expectations para validar os dados no pipeline (esquema, tipos de dados, valores duplicados).
   - Adicionar validações com Pandera para processamentos em Python.

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

---

## Estrutura de Diretórios

```plaintext
project/
├── dags/                    # DAGs do Airflow
├── dbt/                     # Configuração e modelos dbt
├── docker/                  # Dockerfiles para diferentes componentes
│   ├── airflow/             # Configuração do Airflow
│   ├── python/              # Imagem personalizada para Python
├── docs/                    # Arquivos de documentação (MkDocs)
├── src/                     # Código-fonte Python
│   ├── ingestion/           # Scripts para ingestão de dados
│   ├── transformations/     # Processamentos e validações
│   ├── visualization/       # Código Streamlit
├── tests/                   # Testes automatizados (pytest)
├── poetry.lock        # Gerado pelo Poetry
├── pyproject.toml           # Configuração do Poetry
└── docker-compose.yml       # Orquestração dos serviços
```

