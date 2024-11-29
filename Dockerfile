# Use a imagem base do Python
FROM python:3.12.5-slim

# Instale dependências e pacotes necessários
RUN pip install poetry

# Defina o diretório de trabalho no container
WORKDIR /src

# Copie o código do host para o container
COPY ./src /src
COPY ./pyproject.toml /
COPY ./poetry.lock /

# Instale as dependências do Poetry
RUN poetry install --no-dev

RUN chmod +x /src/main.py

# Defina o comando padrão para rodar o script Python
CMD ["poetry", "run", "python", "main.py", "--request_type", "teams"]