"""
This module contains classes and methods for interacting with football competitions APIs 
and processing the retrieved data. It includes functionality for retrieving competition 
details, matches, and storing processed data into a PostgreSQL database.
"""

from typing import Dict, Any
import pandas as pd
import json
import os
import datetime

from utils.football_api import FootballAPIBase
from utils.processor import Processor
from utils.database import Database
from utils.queries import create_queries 
from contracts.competitions_contract import CompetitionsResponse


class CompetitionsAPI(FootballAPIBase):
    """
    Handles API interactions for retrieving football competition data.
    """
    def get_competitions(self, plan: str = "TIER_ONE") -> Dict[str, Any]:
        """
        Retrieves all available competitions based on the specified plan.

        Args:
            plan (str): Competition tier (e.g., TIER_ONE, TIER_TWO).

        Returns:
            Dict[str, Any]: A dictionary containing competition data.
        """
        return self._make_request("competitions", params={"plan": plan})

    def get_competition_by_id(self, competition_id: int) -> Dict[str, Any]:
        """
        Retrieves details for a specific competition.

        Args:
            competition_id (int): The unique ID of the competition.

        Returns:
            Dict[str, Any]: A dictionary containing the competition details.
        """
        return self._make_request(f"competitions/{competition_id}")

    def get_matches(self, competition_id: int) -> Dict[str, Any]:
        """
        Retrieves all matches for a specific competition.

        Args:
            competition_id (int): The unique ID of the competition.

        Returns:
            Dict[str, Any]: A dictionary containing match data.
        """
        return self._make_paginated_request(f"competitions/{competition_id}/matches")
    
class CompetitionsProcessor(Processor):
    """
    Processes competition data fetched from the API and stores it in a database.
    """
    def __init__(self, api_connection: CompetitionsAPI, schema = 'RAW', table = None):
        """
        Initializes the CompetitionsProcessor with the API connection and database details.

        Args:
            api_connection: The API connection instance.
            schema (str, optional): The database schema where data will be stored. Default is 'RAW'.
            table (str, optional): The target database table. Default is None.
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
        Processes competition data by fetching, transforming, and loading it into the database.

        Returns:
            None
        """
        self.logger.info(f"Start Processing - {self.table}")
        self.logger.info("Dataframe from response:")
        competitions_data = CompetitionsResponse(**self.api_connection.get_competitions())

        # Convertendo para dicionário e depois criando o DataFrame
        competitions_dict = [comp.model_dump() for comp in competitions_data.competitions]
        df = pd.DataFrame(competitions_dict)
        
        # Converte as colunas 'area' e 'current_season' para JSON (se não forem nulas)
        df['area'] = df['area'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else None)
        df['current_season'] = df['current_season'].apply(lambda x: json.dumps(x, default=str) if isinstance(x, dict) else None)

        load_timesamp = datetime.datetime.now(datetime.timezone.utc).isoformat() 
        
        metadata = {
            "load_timestamp": [load_timesamp] * len(df),
        }

        metadata_df = pd.DataFrame(metadata)

        df_with_metadata = pd.concat([df, metadata_df], axis=1)
    
        # Verificando o DataFrame
        self.logger.info(df_with_metadata)
        self.logger.info(f"Writing to Database - {self.table}:")
        self._write_to_db(df_with_metadata)

    def _write_to_db(self, df: pd.DataFrame) -> None:
        """
        Writes the processed DataFrame to the specified database table.

        Args:
            df (pd.DataFrame): The processed DataFrame to be inserted into the database.

        Returns:
            None
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
