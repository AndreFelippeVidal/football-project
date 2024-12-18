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
from contracts.matches_today_contract import MatchesTodayResponse


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

        Returns:
            Dict[str, Any]: A dictionary containing match data.
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
        """
        self.logger.info(f"Start Processing - {self.table}")

        matches_data = []
        
        self.logger.info(f'Retrieving data for matches today.')
        match_data = MatchesTodayResponse(**self.api_connection.get_matches_today())
        # Convertendo para dicionário e depois criando o DataFrame
        matches_dict = [comp.model_dump() for comp in match_data.matches]
        df = pd.DataFrame(matches_dict)
        df['date_from'] = match_data.filters['dateFrom']

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
   
        df_with_metadata.to_csv('matches_today', index=False)
        self.logger.info(f"Writing to Database - {self.table}:")
        self._write_to_db(df_with_metadata)

    def _write_to_db(self, df: pd.DataFrame) -> None:
        """
        Writes the processed DataFrame to the database.

        Args:
            df (pd.DataFrame): The DataFrame to write to the database.
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
