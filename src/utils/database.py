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
        """
        Initializes the Database connection parameters.

        Args:
            db_name (str): The name of the database.
            user (str): The username to connect to the database.
            password (str): The password for the user.
            host (str): The host of the database server.
            port (int, optional): The port of the database server. Default is 5432.
        """
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None

    def connect(self):
        """
        Establishes a connection to the PostgreSQL database.
        """
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
                    #cursor_factory=RealDictCursor  # Return the data as a dict
                )
                
            except psycopg2.Error as e:
                print(f"Error connecting to PostgreSQL: {e}")
                raise

    def close(self):
        """
        Closes the connection to the PostgreSQL database.
        """
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
            except psycopg2.Error as e:
                print(f"Error closing connection: {e}")

    @contextmanager
    def cursor(self):
        """
        Manages the database cursor context, automatically handling commits and rollbacks.

        Yields:
            cursor: A database cursor for executing SQL queries.
        """
        self.connect()
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(f"Error executing query: {e}")
            raise
        finally:
            cursor.close()

    def insert(self, table, data):
        """
        Inserts data into a specified table.

        Args:
            table (str): The name of the table.
            data (dict): A dictionary of column-value pairs to insert.
        """
        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({values})"

        with self.cursor() as cursor:
            cursor.execute(query, tuple(data.values()))

    def select(self, table, columns='*', where=None):
        """
        Selects data from a specified table.

        Args:
            table (str): The name of the table.
            columns (str, optional): The columns to select, separated by commas. Defaults to '*' (all columns).
            where (str, optional): An optional SQL condition for filtering results.

        Returns:
            list[dict]: A list of rows returned from the query.
        """
        query = f"SELECT {columns} FROM {table}"
        if where:
            query += f" WHERE {where}"

        with self.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def delete(self, table, where):
        """
        Deletes data from a specified table.

        Args:
            table (str): The name of the table.
            where (str): The condition for deleting records. This is required to prevent deleting all records.
        """
        if not where:
            raise ValueError("The WHERE clause is required to avoid deleting all records.")
        
        query = f"DELETE FROM {table} WHERE {where}"

        with self.cursor() as cursor:
            cursor.execute(query)

    def execute_query(self, query, params=None):
        """
        Executes a generic SQL query.

        Args:
            query (str): The SQL query to execute.
            params (tuple | list, optional): Parameters to be passed to the query. Defaults to None.

        Returns:
            list[dict]: The query result, if it's a SELECT query.
        """
        with self.cursor() as cursor:
            cursor.execute(query, params)
            # Return results for SELECT command
            if query.strip().lower().startswith("select"):
                return cursor.fetchall()

    def validate_table_exists(self, schema, table, create_table_sql):
        """
        Validates whether the schema and table exist in the database, creating them if necessary.

        Args:
            schema (str): The name of the schema.
            table (str): The name of the table.
            create_table_sql (str): The SQL command to create the table if it doesn't exist.
        """
        logging.info("Starting table/schema validation")
        # Verify if the schema exists
        check_schema_query = """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.schemata
            WHERE schema_name = %s
        )
        """
        
        with self.cursor() as cursor:
            # Verify if the schema exists
            cursor.execute(check_schema_query, (schema,))
            schema_exists = cursor.fetchone()[0]  # Access tuple value

            if not schema_exists:
                print(f"Schema '{schema}' not found. Creating...")
                cursor.execute(f"CREATE SCHEMA {schema};")
                print(f"Schema '{schema}' successfully created!")

            # Verify if the table exist inside schema
            check_table_query = """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = %s AND table_name = %s
            )
            """
            cursor.execute(check_table_query, (schema, table))
            table_exists = cursor.fetchone()[0] 

            if not table_exists:
                print(f"Tabela '{schema}.{table}' not found. Creating...")
                cursor.execute(create_table_sql)
                print(f"Tabela '{schema}.{table}' created successfully!")

    def insert_pandas_bulk(self, df: pd.DataFrame, table_name: str):
        """
        Inserts the data from a Pandas DataFrame into a specified table in bulk.

        Args:
            df (pd.DataFrame): The DataFrame containing the data to be inserted.
            table_name (str): The name of the target table.
        """
        logging.info("Starting dataframe bulk load")
        try:
            # Generate tuple list from Dataframe
            records = df.values.tolist()
            # Generate a placeholder string for SQL
            columns = ', '.join(df.columns)
            placeholders = ', '.join(['%s'] * len(df.columns))
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            # Connect and execute INSERT command
            with self.cursor() as cursor:
                cursor.executemany(insert_query, records)
                cursor.close()
            print(f"{len(records)} records inserted successfully!")
        except Exception as e:
            print(f"Error to insert records: {e}")
            raise

# Example
if __name__ == "__main__":
    db = Database(
        db_name=os.getenv('PG_DB'),
        user=os.getenv('PG_USER'),
        password=os.getenv('PG_PASS'),
        host=os.getenv('PG_HOST'),
        port=5432
    )

    # Table definition
    schema = "raw"
    table = "example_table"
    create_table_sql = f"""
    CREATE TABLE {schema}.{table} (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    # Verify and create table if exists
    db.validate_table_exists(schema, table, create_table_sql)

    # Insert data
    db.insert("raw.example_table", {"name": "John Doe"})

    # Select data
    users = db.select("raw.example_table", columns="id, name")
    print(users)

    # Delete data
    db.delete("raw.example_table", "name = 'John Doe'")

    users = db.select("raw.example_table", columns="id, name")
    print(users)

    db.execute_query('DROP TABLE raw.example_table')

    db.close()
