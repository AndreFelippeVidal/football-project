"""
This module provides classes for interacting with and processing team data 
from a football API, including fetching matches details and integrating them into a database.
"""
from utils.football_api import FootballAPIBase
from typing import Dict, Any
import pandas as pd
import json
import os
import datetime
import time

from utils.processor import Processor
from utils.database import Database
from utils.queries import create_queries 
from contracts.matches_contract import MatchesTodayResponse


pd.set_option('display.max_colwidth', None)

class MatchesAPI(FootballAPIBase):
    """
    Handles API interactions for fetching team-related data.

    Methods:
        - get_matches_today: Fetches all the matches that will happen today.
    """
    def get_matches_today(self) -> Dict[str, Any]:
        """
        Retrieves all matches for your competition tier today.

        Fetches match data from the football API and returns it in a dictionary format.

        Returns:
            Dict[str, Any]: A dictionary containing match data, with details of matches scheduled for today.

        Example:
            {
                "matches": [
                    {"match_id": 123, "home_team": "Team A", "away_team": "Team B", ...},
                    {"match_id": 124, "home_team": "Team C", "away_team": "Team D", ...}
                ]
            }
        """
        return self._make_request(f"matches")

class MatchesProcessor(Processor):
    """
    Processes and integrates team data from the API into the database.

    Attributes:
        api_connection: The API connection used for fetching data.
        schema (str): Database schema to use.
        table (str): Database table to insert data into.

    Methods:
        - process: Fetches, transforms, and loads team data into the database.
    """
    def __init__(self, api_connection: MatchesAPI, schema = 'RAW', table = None):
        """
        Initializes the MatchesProcessor.

        Args:
            api_connection: The API connection used for fetching data.
            schema (str, optional): The schema to use in the database. Defaults to 'RAW'.
            table (str, optional): The table to insert data into. Defaults to None.
        """
        super().__init__(api_connection, self.__class__.__name__)

        if schema:
            self.schema = schema
        if table:
            self.table = table

        self.db = Database(
            db_name=os.getenv('PG_DB'),
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASS'),
            host=os.getenv('PG_HOST'),
            port=5432
        )

    def process(self) -> None:
        """
        Processes team data by fetching it from the API, transforming it, 
        and loading it into the database.

        This method fetches match data for today, transforms it into a DataFrame, 
        applies necessary transformations, and loads it into the specified database 
        table along with metadata like load timestamp.

        The method performs the following steps:
        - Fetches match data using the API.
        - Converts the data into a pandas DataFrame.
        - Transforms relevant columns into JSON format.
        - Adds a load timestamp column.
        - Loads the final DataFrame into the database.

        Example:
            matches_processor = MatchesProcessor(api_connection=matches_api, schema='RAW', table='matches')
            matches_processor.process()
        """
        self.logger.info(f"Start Processing - {self.table}")

        matches_data = []
        
        self.logger.info(f'Retrieving data for matches today.')
        match_data = MatchesTodayResponse(**self.api_connection.get_matches_today())
        # Convertendo para dicionário e depois criando o DataFrame
        matches_dict = [comp.model_dump() for comp in match_data.matches]
        df = pd.DataFrame(matches_dict)
        df['date_from'] = match_data.filters.date_from

        matches_data.append(df)

        final_matches_df = pd.concat(matches_data)
        
        # Converte as colunas 'area' e 'current_season' para JSON (se não forem nulas)
        final_matches_df['area'] = final_matches_df['area'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else None)
        final_matches_df['competition'] = final_matches_df['competition'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else None)
        final_matches_df['season'] = final_matches_df['season'].apply(lambda x: json.dumps(x, default=str) if isinstance(x, dict) else None)
        final_matches_df['home_team'] = final_matches_df['home_team'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else None)
        final_matches_df['away_team'] = final_matches_df['away_team'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else None)
        final_matches_df['score'] = final_matches_df['score'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else None)
        final_matches_df['odds'] = final_matches_df['odds'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else None)
        final_matches_df['referees'] = final_matches_df['referees'].apply(lambda x: json.dumps([element for element in x if isinstance(element, dict)], default=str) if isinstance(x, list) else None)
        
        load_timesamp = datetime.datetime.now(datetime.timezone.utc).isoformat() 
        
        metadata = {
            "load_timestamp": [load_timesamp] * len(final_matches_df),
        }

        metadata_df = pd.DataFrame(metadata, index=final_matches_df.index)

        df_with_metadata = pd.concat([final_matches_df, metadata_df], axis=1)
   
        # df_with_metadata.to_csv('matches_today', index=False)
        self.logger.info(f"Writing to Database - {self.table}:")
        self._write_to_db(df_with_metadata)

    def _write_to_db(self, df: pd.DataFrame) -> None:
        """
        Writes the processed DataFrame to the database.

        This method executes the necessary SQL queries to insert the data into the specified 
        database table after validating that the table exists and truncating the existing data.

        Args:
            df (pd.DataFrame): The DataFrame to write to the database.

        Raises:
            Exception: If there is an issue with the database connection or query execution.
        """

        query = getattr(create_queries, self.table.upper()).format(
            schema=self.schema,
            table=self.table
        )
        # Verificar e criar a tabela se necessário
        self.db.validate_table_exists(self.schema, self.table, query)
        self.db.execute_query(
            create_queries.TRUNCATE_TABLE.format(
                schema=self.schema,
                table=self.table
            )
        )
        self.db.insert_pandas_bulk(df,f'{self.schema}.{self.table}')
