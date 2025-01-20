import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os
from dotenv import load_dotenv
import pandas as pd
import logging

load_dotenv()

class Database:
    def __init__(self, db_name, user, password, host, port=5432):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None

    def connect(self):
        """Estabelece a conexão com o banco de dados."""
        if not self.connection:
            try:
                print(f'db: {self.db_name}')
                print(f'user: {self.user}')
                print(f'host: {self.host}')
                self.connection = psycopg2.connect(
                    dbname=self.db_name,
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    port=self.port,
                    #cursor_factory=RealDictCursor  # Retorna os resultados como dicionário
                )
                
            except psycopg2.Error as e:
                print(f"Erro ao conectar ao PostgreSQL: {e}")
                raise

    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
            except psycopg2.Error as e:
                print(f"Erro ao fechar a conexão: {e}")

    @contextmanager
    def cursor(self):
        """Gerencia o cursor automaticamente."""
        self.connect()
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(f"Erro ao executar query: {e}")
            raise
        finally:
            cursor.close()

    def insert(self, table, data):
        """Insere dados em uma tabela.
        Args:
            table (str): Nome da tabela.
            data (dict): Dados a serem inseridos (coluna: valor).
        """
        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({values})"

        with self.cursor() as cursor:
            cursor.execute(query, tuple(data.values()))

    def select(self, table, columns='*', where=None):
        """Seleciona dados de uma tabela.
        Args:
            table (str): Nome da tabela.
            columns (str): Colunas a serem retornadas, separadas por vírgulas.
            where (str): Condição SQL opcional.
        Returns:
            list[dict]: Resultados da query.
        """
        query = f"SELECT {columns} FROM {table}"
        if where:
            query += f" WHERE {where}"

        with self.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def delete(self, table, where):
        """Exclui dados de uma tabela.
        Args:
            table (str): Nome da tabela.
            where (str): Condição SQL obrigatória.
        """
        if not where:
            raise ValueError("A cláusula WHERE é obrigatória para evitar exclusões completas.")
        
        query = f"DELETE FROM {table} WHERE {where}"

        with self.cursor() as cursor:
            cursor.execute(query)

    def execute_query(self, query, params=None):
        """Executa uma query SQL genérica.
        Args:
            query (str): Comando SQL a ser executado.
            params (tuple | list, optional): Parâmetros para a query. Defaults to None.
        Returns:
            list[dict]: Resultados da query, se houver (para SELECTs).
        """
        with self.cursor() as cursor:
            cursor.execute(query, params)
            # Retorna resultados apenas para comandos SELECT
            if query.strip().lower().startswith("select"):
                return cursor.fetchall()

    def validate_table_exists(self, schema, table, create_table_sql):
        """Verifica se o esquema e a tabela existem e cria-os se necessário.
        Args:
            schema (str): Nome do esquema.
            table (str): Nome da tabela.
            create_table_sql (str): Comando SQL para criar a tabela.
        """
        logging.info("Starting table/schema validation")
        # Verifica se o schema existe
        check_schema_query = """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.schemata
            WHERE schema_name = %s
        )
        """
        
        with self.cursor() as cursor:
            # Verifica se o schema existe
            cursor.execute(check_schema_query, (schema,))
            schema_exists = cursor.fetchone()[0]  # Acessa o valor da tupla

            if not schema_exists:
                print(f"Schema '{schema}' não encontrado. Criando...")
                cursor.execute(f"CREATE SCHEMA {schema};")
                print(f"Schema '{schema}' criado com sucesso!")

            # Agora verifica se a tabela existe no schema
            check_table_query = """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = %s AND table_name = %s
            )
            """
            cursor.execute(check_table_query, (schema, table))
            table_exists = cursor.fetchone()[0]  # Acessa o valor da tupla

            if not table_exists:
                print(f"Tabela '{schema}.{table}' não encontrada. Criando...")
                cursor.execute(create_table_sql)
                print(f"Tabela '{schema}.{table}' criada com sucesso!")

    def insert_pandas_bulk(self, df: pd.DataFrame, table_name: str):
        """Insere os dados de um DataFrame em massa na tabela especificada"""
        logging.info("Starting dataframe bulk load")
        try:
            # Gerar a lista de tuplas a partir do DataFrame
            records = df.values.tolist()
            # Gerar a string de placeholders para o SQL
            columns = ', '.join(df.columns)
            placeholders = ', '.join(['%s'] * len(df.columns))
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            # Conectar e executar o comando de inserção
            with self.cursor() as cursor:
                cursor.executemany(insert_query, records)
                cursor.close()
            print(f"{len(records)} registros inseridos com sucesso!")
        except Exception as e:
            print(f"Erro ao inserir registros: {e}")
            raise

# Exemplo de uso
if __name__ == "__main__":
    db = Database(
        db_name=os.getenv('PG_DB'),
        user=os.getenv('PG_USER'),
        password=os.getenv('PG_PASS'),
        host=os.getenv('PG_HOST'),
        port=5432
    )

    # Definição da tabela
    schema = "raw"
    table = "example_table"
    create_table_sql = f"""
    CREATE TABLE {schema}.{table} (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    # Verificar e criar a tabela se necessário
    db.validate_table_exists(schema, table, create_table_sql)

    # Inserir dados
    db.insert("raw.example_table", {"name": "John Doe"})

    # Selecionar dados
    users = db.select("raw.example_table", columns="id, name")
    print(users)

    # Excluir dados
    db.delete("raw.example_table", "name = 'John Doe'")

    users = db.select("raw.example_table", columns="id, name")
    print(users)

    db.execute_query('DROP TABLE raw.example_table')

    db.close()
