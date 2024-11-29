import click, os, json
from datetime import datetime
import pandas as pd
from utils.competitions_api import CompetitionsAPI
from utils.teams_api import TeamsAPI
from utils.database import Database
from contracts.competitions_contract import CompetitionsResponse
from dotenv import load_dotenv

load_dotenv()

# if __name__ == "__main__":
#     # Substitua "SUA_CHAVE" pela sua chave gerada no site da API
#     token = None

#     # Testando CompetitionsAPI
#     competitions_api = CompetitionsAPI(token=token)
#     print("Competições Disponíveis:")
#     print(competitions_api.get_competitions())
#     competitions_api.close()

#     competitions_api = CompetitionsAPI(token=token)
#     print("\nDetalhes de uma Competição:")
#     print(competitions_api.get_competition_by_id(2001))  # Exemplo: ID da Champions League
#     competitions_api.close()

#     # Testando TeamsAPI
#     teams_api = TeamsAPI(token=token)
#     print("\nTimes de uma Competição:")
#     print(teams_api.get_teams(2001))  # Exemplo: Times da Champions League
#     teams_api.close()

#     teams_api = TeamsAPI(token=token)
#     print("\nDetalhes de um Time:")
#     print(teams_api.get_team_by_id(64))  # Exemplo: ID do Liverpool
#     teams_api.close()

@click.command()
@click.option('--request_type', type=click.Choice(['teams', 'competitions'], case_sensitive=False), help="Tipo de requisição a ser feita")
def main(request_type):
    """
    Função principal que direciona a requisição com base no parâmetro passado via CLI.
    """
    if request_type == 'teams':
        teams_api = TeamsAPI(token=None)
        print("\nTimes de uma Competição:")
        print(teams_api.get_teams(2001)) 
    elif request_type == 'competitions':
        competitions_api = CompetitionsAPI(token=None)
        print("Competições Disponíveis:")
        # print(competitions_api.get_competitions())
        competitions_data = CompetitionsResponse(**competitions_api.get_competitions())
        #print(competitions_data)
        # Convertendo para dicionário e depois criando o DataFrame
        competitions_dict = [comp.model_dump() for comp in competitions_data.competitions]
        df = pd.DataFrame(competitions_dict)
        
        # Converte as colunas 'area' e 'current_season' para JSON (se não forem nulas)
        df['area'] = df['area'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else None)
        df['current_season'] = df['current_season'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else None)
        
        

        # Verificando o DataFrame
        print(df)

        db = Database(
            db_name=os.getenv('PG_DB'),
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASS'),
            host=os.getenv('PG_HOST'),
            port=5432
        )
        db.execute_query('DROP TABLE raw.competitions')
        schema = "raw"
        table = "competitions"
        create_table_sql = f"""
        CREATE TABLE {schema}.{table} (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            area JSONB NOT NULL,
            code VARCHAR(50),
            type VARCHAR(50),
            emblem VARCHAR(255),
            plan VARCHAR(50),
            current_season JSONB NOT NULL,
            number_of_available_seasons INT NOT NULL,
            last_updated TIMESTAMP NOT NULL
        );
        """
        
        # Verificar e criar a tabela se necessário
        db.validate_table_exists(schema, table, create_table_sql)
        db.insert_pandas_bulk(df,f'{schema}.{table}')

        
    else:
        print("Tipo de requisição inválido!")

if __name__ == '__main__':
    main()