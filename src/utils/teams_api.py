"""
This module provides classes for interacting with and processing team data 
from a football API, including fetching team details and integrating them into a database.
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
from contracts.teams_contract import TeamsResponse
from contracts.matches_contract import MatchesTodayResponse

pd.set_option('display.max_colwidth', None)

class TeamsAPI(FootballAPIBase):
    """
    Handles API interactions for fetching team-related data.

    Methods:
        - get_teams: Fetches teams of a specific competition.
        - get_team_by_id: Fetches details of a specific team.
    """
    def get_teams(self, competition_id: int) -> Dict[str, Any]:
        """
        Fetches teams participating in a specific competition.

        Args:
            competition_id (int): The ID of the competition to fetch teams from.

        Returns:
            Dict[str, Any]: The API response containing team details.
        """
        return self._make_request(f"competitions/{competition_id}/teams")

    def get_team_by_id(self, team_id: int) -> Dict[str, Any]:
        """
        Fetches details of a specific team.

        Args:
            team_id (int): The ID of the team to fetch details for.

        Returns:
            Dict[str, Any]: The API response containing the team's details.
        """
        return self._make_request(f"teams/{team_id}")
    
    def get_team_upcoming_matches(self, team_id: int) -> Dict[str, Any]:
        """
        Fetches upcoming matches of a specific team.

        Args:
            team_id (int): The ID of the team to fetch details for.

        Returns:
            Dict[str, Any]: The API response containing the team's upcoming matches details.
        """
        return self._make_request(f"teams/{team_id}/matches?status=SCHEDULED&limit=10")

class TeamsProcessor(Processor):
    """
    Processes and integrates team data from the API into the database.

    Attributes:
        api_connection: The API connection used for fetching data.
        competition_ids (list): List of competition IDs for which to process teams.
        schema (str): Database schema to use.
        table (str): Database table to insert data into.

    Methods:
        - process: Fetches, transforms, and loads team data into the database.
    """
    def __init__(self, api_connection: TeamsAPI, competition_ids: list, schema = 'RAW', table = None):
        """
        Initializes the TeamsProcessor.

        Args:
            api_connection: The API connection used for fetching data.
            competition_ids (list): List of competition IDs to process.
            schema (str, optional): The schema to use in the database. Defaults to 'RAW'.
            table (str, optional): The table to insert data into. Defaults to None.
        """
        super().__init__(api_connection, self.__class__.__name__)

        if schema:
            self.schema = schema
        if table:
            self.table = table

        self.competition_ids = competition_ids

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

        teams_data = []

        competition_ids_result = self.db.select(table=f'{self.schema}.competitions', columns='distinct id')
        competition_ids = [row[0] for row in competition_ids_result]

        self.logger.info(f"Competition IDs to be retrieved: {competition_ids}")
        
        for competition_id in competition_ids:
            self.logger.info(f'Retrieving data for competition id: {competition_id}')
            team_data = TeamsResponse(**self.api_connection.get_teams(competition_id))
            # Convertendo para dicionário e depois criando o DataFrame
            teams_dict = [comp.model_dump() for comp in team_data.teams]
            df = pd.DataFrame(teams_dict)
            df['competition_id'] = competition_id

            teams_data.append(df)

        final_competition_teams_df = pd.concat(teams_data)
        
        # Converte as colunas 'area' e 'current_season' para JSON (se não forem nulas)
        final_competition_teams_df['area'] = final_competition_teams_df['area'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else None)
        final_competition_teams_df['squad'] = final_competition_teams_df['squad'].apply(lambda x: json.dumps([element for element in x if isinstance(element, dict)], default=str) if isinstance(x, list) else None)
        final_competition_teams_df['staff'] = final_competition_teams_df['staff'].apply(lambda x: json.dumps([element for element in x if isinstance(element, dict)], default=str) if isinstance(x, list) else None)
        final_competition_teams_df['running_competitions'] = final_competition_teams_df['running_competitions'].apply(lambda x: json.dumps([element for element in x if isinstance(element, dict)]) if isinstance(x, list) else None)
        final_competition_teams_df['coach'] = final_competition_teams_df['coach'].apply(lambda x: json.dumps(x, default=str) if isinstance(x, dict) else None)
        final_competition_teams_df.rename(columns={'id': 'team_id'}, inplace=True)

        load_timesamp = datetime.datetime.now(datetime.timezone.utc).isoformat() 
        
        metadata = {
            "load_timestamp": [load_timesamp] * len(final_competition_teams_df),
        }

        metadata_df = pd.DataFrame(metadata, index=final_competition_teams_df.index)

        df_with_metadata = pd.concat([final_competition_teams_df, metadata_df], axis=1)
    
        # Verificando o DataFrame
        # self.logger.info(df_with_metadata)
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

class TeamUpcomingMatchesProcessor(Processor):
    """
    Processes and integrates team data from the API into the database.

    Attributes:
        api_connection: The API connection used for fetching data.
        schema (str): Database schema to use.
        table (str): Database table to insert data into.

    Methods:
        - process: Fetches, transforms, and loads team data into the database.
    """
    def __init__(self, api_connection: TeamsAPI, schema = 'RAW', table = None):
        """
        Initializes the TeamsProcessor.

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

        teams_matches_data = []

        teams_ids_result = self.db.select(table=f'{self.schema}.teams', columns='distinct team_id')
        teams_ids = [row[0] for row in teams_ids_result]
        # teams_ids = [86]

        self.logger.info(f"Team IDs to be retrieved: {teams_ids}")
        
        for team_id in teams_ids:
            self.logger.info(f'Retrieving data for team id: {team_id}')
            team_matches_data = MatchesTodayResponse(**self.api_connection.get_team_upcoming_matches(team_id))
            # Convertendo para dicionário e depois criando o DataFrame
            teams_matches_dict = [comp.model_dump() for comp in team_matches_data.matches]
            df = pd.DataFrame(teams_matches_dict)
            df['date_from'] = team_matches_data.filters.date_from
            df['date_to'] = team_matches_data.filters.date_to

            teams_matches_data.append(df)

        final_teams_matches_df = pd.concat(teams_matches_data)
        
        # Converte as colunas 'area' e 'season' para JSON (se não forem nulas)
        final_teams_matches_df['area'] = final_teams_matches_df['area'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else None)
        final_teams_matches_df['competition'] = final_teams_matches_df['competition'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else None)
        final_teams_matches_df['season'] = final_teams_matches_df['season'].apply(lambda x: json.dumps(x, default=str) if isinstance(x, dict) else None)
        final_teams_matches_df['home_team'] = final_teams_matches_df['home_team'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else None)
        final_teams_matches_df['away_team'] = final_teams_matches_df['away_team'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else None)
        final_teams_matches_df['score'] = final_teams_matches_df['score'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else None)
        final_teams_matches_df['odds'] = final_teams_matches_df['odds'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else None)
        final_teams_matches_df['referees'] = final_teams_matches_df['referees'].apply(lambda x: json.dumps([element for element in x if isinstance(element, dict)], default=str) if isinstance(x, list) else None)

        load_timesamp = datetime.datetime.now(datetime.timezone.utc).isoformat() 
        
        metadata = {
            "load_timestamp": [load_timesamp] * len(final_teams_matches_df),
        }

        metadata_df = pd.DataFrame(metadata, index=final_teams_matches_df.index)

        df_with_metadata = pd.concat([final_teams_matches_df, metadata_df], axis=1)
    
        df_with_metadata.to_csv('teams_matches', index=False)
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