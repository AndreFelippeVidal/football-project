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
from contracts.competitions_standings_contract import CompetitionStandingsResponse
from contracts.competitions_top_scorers_contract import TopScorersResponse

pd.set_option('display.max_colwidth', None)

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

    def get_standings(self, competition_id: int, season: int = None) -> Dict[str, Any]:
        """
        Retrieves all matches for a specific competition.

        Args:
            competition_id (int): The unique ID of the competition.

        Returns:
            Dict[str, Any]: A dictionary containing match data.
        """
        if not season:
            return self._make_request(f"competitions/{competition_id}/standings")
        else:    
            return self._make_request(f"competitions/{competition_id}/standings?season={season}")
    
    def get_top_scorers(self, competition_id: int, season: int = None) -> Dict[str, Any]:
        """
        Retrieves top scorers for a specific competition.

        Args:
            competition_id (int): The unique ID of the competition.

        Returns:
            Dict[str, Any]: A dictionary containing top scorers data.
        """
        if not season:
            return self._make_request(f"competitions/{competition_id}/scorers")
        else:    
            return self._make_request(f"competitions/{competition_id}/scorers?season={season}")
    
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


class CompetitionsDetailsProcessor(Processor):
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

        if self.table == 'competitions_standings':
            standings_data = []

            actual_year = datetime.datetime.now().year

            competition_ids_result = self.db.select(table=f'{self.schema}.competitions', columns='distinct id')
            competition_ids = [row[0] for row in competition_ids_result]

            self.logger.info(f"Competition IDs Standings to be retrieved: {competition_ids}")
            
            for season in range(actual_year-2, actual_year+1):
                self.logger.info(f'Retrieving data for season: {season}')
                for competition_id in competition_ids:
                    self.logger.info(f'Retrieving data for competition id: {competition_id}')
                    ## For Cup competitions like FIFA World Cup/UEFA Champions League/European Championship/Libertadores different logic is needed
                    if competition_id not in [2000,2001,2018,2152]:
                        try:
                            standing_data = CompetitionStandingsResponse(**self.api_connection.get_standings(competition_id=competition_id, season=season))
                        except Exception as e: 
                            self.logger.error(f'Not able to retrieve data for competition_id: {competition_id} season: {season}. \nReason: {e}')
                            continue
                    elif season == actual_year:
                        try:
                            standing_data = CompetitionStandingsResponse(**self.api_connection.get_standings(competition_id=competition_id))
                        except Exception as e: 
                            self.logger.error(f'Not able to retrieve data for competition_id: {competition_id} season: {season}. \nReason: {e}')
                            continue
                    else:
                        #self.logger.info(f"Something happened that didn't met for conditions")
                        continue
                    # Convertendo para dicionário e depois criando o DataFrame
                    standings_dict = [item.model_dump() for item in standing_data.standings]
                    df = pd.DataFrame(standings_dict[0]['table'])
                    df['competition_id'] = competition_id
                    df['season'] = standing_data.filters['season']
                    df['season_info'] = standing_data.season.model_dump_json()

                    standings_data.append(df)

            final_competition_standings_df = pd.concat(standings_data)
                
            # # Converte a colunas 'team' (se não for nula)
            final_competition_standings_df['team'] = final_competition_standings_df['team'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else None)

            load_timesamp = datetime.datetime.now(datetime.timezone.utc).isoformat() 
            
            metadata = {
                "load_timestamp": [load_timesamp] * len(final_competition_standings_df),
            }

            metadata_df = pd.DataFrame(metadata, index=final_competition_standings_df.index)

            df_with_metadata = pd.concat([final_competition_standings_df, metadata_df], axis=1)
        
            # df_with_metadata.to_csv('competition_details', index=False)
            self.logger.info(f"Writing to Database - {self.table}:")
            self._write_to_db(df_with_metadata)
        
        elif self.table == 'competitions_top_scorers':
            top_scorers = []

            actual_year = datetime.datetime.now().year

            competition_ids_result = self.db.select(table=f'{self.schema}.competitions', columns='distinct id')
            competition_ids = [row[0] for row in competition_ids_result]

            self.logger.info(f"Competition IDs Standings to be retrieved: {competition_ids}")
            
            for season in range(actual_year-2, actual_year+1):
                self.logger.info(f'Retrieving data for season: {season}')
                for competition_id in competition_ids:
                    self.logger.info(f'Retrieving data for competition id: {competition_id}')
                    ## For Cup competitions like FIFA World Cup/UEFA Champions League/European Championship/Libertadores different logic is needed
                    if competition_id not in [2000,2001,2018,2152]:
                        try:
                            top_scorer_data = TopScorersResponse(**self.api_connection.get_top_scorers(competition_id=competition_id, season=season))
                        except Exception as e: 
                            self.logger.error(f'Not able to retrieve data for competition_id: {competition_id} season: {season}. \nReason: {e}')
                            continue
                    elif season == actual_year:
                        try: 
                            top_scorer_data = TopScorersResponse(**self.api_connection.get_top_scorers(competition_id=competition_id))
                        except Exception as e: 
                            self.logger.error(f'Not able to retrieve data for competition_id: {competition_id} season: {season}. \nReason: {e}')
                            continue
                    else:
                        continue
                    # Convertendo para dicionário e depois criando o DataFrame
                    top_scorers_dict = [item.model_dump() for item in top_scorer_data.scorers]
                    df = pd.DataFrame(top_scorers_dict)
                    df['competition_id'] = competition_id
                    df['season'] = top_scorer_data.filters['season']
                    df['season_info'] = top_scorer_data.season.model_dump_json()

                    top_scorers.append(df)

            final_competition_top_scorers_df = pd.concat(top_scorers)
                
            # # Converte a colunas 'team' (se não for nula)
            final_competition_top_scorers_df['team'] = final_competition_top_scorers_df['team'].apply(lambda x: json.dumps(x, default=str) if isinstance(x, dict) else None)
            final_competition_top_scorers_df['player'] = final_competition_top_scorers_df['player'].apply(lambda x: json.dumps(x, default=str) if isinstance(x, dict) else None)

            load_timesamp = datetime.datetime.now(datetime.timezone.utc).isoformat() 
            
            metadata = {
                "load_timestamp": [load_timesamp] * len(final_competition_top_scorers_df),
            }

            metadata_df = pd.DataFrame(metadata, index=final_competition_top_scorers_df.index)

            df_with_metadata = pd.concat([final_competition_top_scorers_df, metadata_df], axis=1)
        
            # df_with_metadata.to_csv('competition_top_scorers', index=False)
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