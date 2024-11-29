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

pd.set_option('display.max_colwidth', None)

class TeamsAPI(FootballAPIBase):
    def get_teams(self, competition_id: int) -> Dict[str, Any]:
        """
        Retorna os times de uma competição específica.
        """
        return self._make_request(f"competitions/{competition_id}/teams")

    def get_team_by_id(self, team_id: int) -> Dict[str, Any]:
        """
        Retorna detalhes de um time específico.
        """
        return self._make_request(f"teams/{team_id}")

class TeamsProcessor(Processor):
    def __init__(self, api_connection, competition_ids: list, schema = 'RAW', table = None):
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

        query = getattr(create_queries, self.table.upper()).format(
            schema=self.schema,
            table=self.table
        )
        # Verificar e criar a tabela se necessário
        self.db.validate_table_exists(self.schema, self.table, query)
        self.db.insert_pandas_bulk(df,f'{self.schema}.{self.table}')
