# Use a imagem base do Python
FROM python:3.12.5-slim

# Instale dependências do sistema
RUN apt-get update && apt-get install -y \
    curl build-essential libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instale o Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry


# Defina o diretório de trabalho no container
WORKDIR /src

# Copie o código do host para o container
COPY ../pyproject.toml ../poetry.lock /
RUN poetry config virtualenvs.create false && poetry install --no-root

COPY ./src /src

RUN chmod +x /src/main.py

# Defina o comando padrão para rodar o script Python
CMD ["poetry", "run", "python", "main.py", "--request_type", "teams"]