import click
from utils.competitions_api import CompetitionsAPI, CompetitionsProcessor, CompetitionsDetailsProcessor
from utils.teams_api import TeamsAPI, TeamsProcessor
from contracts.teams_contract import TeamsResponse
from dotenv import load_dotenv

load_dotenv()

@click.command()
@click.option('--request_type', type=click.Choice(['teams', 'competitions','competitions_standings'], case_sensitive=False), help="Tipo de requisição a ser feita")
def main(request_type):
    """
    Função principal que direciona a requisição com base no parâmetro passado via CLI.
    """
    if request_type == 'teams':
        teams_api = TeamsAPI(token=None)
        TeamsProcessor(teams_api, competition_ids=[2001] ,schema='raw', table='teams').process()
    elif request_type == 'competitions':
        competitions_api = CompetitionsAPI(token=None)
        CompetitionsProcessor(competitions_api, schema='raw', table='competitions').process()
    elif request_type == 'competitions_standings':
        competitions_standings_api = CompetitionsAPI(token=None)
        CompetitionsDetailsProcessor(competitions_standings_api, schema='raw', table='competitions_standings').process()
    elif request_type == 'competitions_top_scorers':
        competitions_top_scorers_api = CompetitionsAPI(token=None)
        CompetitionsDetailsProcessor(competitions_top_scorers_api, schema='raw', table='competitions_top_scorers').process()
        
    else:
        print("Tipo de requisição inválido!")

if __name__ == '__main__':
    main()
    #     teams_api = TeamsAPI(token=token)
    #     print("\nDetalhes de um Time:")
    #     print(teams_api.get_team_by_id(64))  # Exemplo: ID do Liverpool

    #     competitions_api = CompetitionsAPI(token=token)
    #     print("\nDetalhes de uma Competição:")
    #     print(competitions_api.get_competition_by_id(2001))  # Exemplo: ID da Champions League
    