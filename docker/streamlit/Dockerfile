# Use uma imagem base leve com Python
FROM python:3.12.5-slim

# Instale dependências do sistema
RUN apt-get update && apt-get install -y \
    curl build-essential libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instale o Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos do Poetry e instale dependências
COPY ../pyproject.toml ../poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-root --only app

# Copie o restante do código da aplicação
COPY ./src/visualization/app.py .

# Exponha a porta padrão do Streamlit
EXPOSE 8501

# Comando para rodar o Streamlit
CMD ["poetry", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
