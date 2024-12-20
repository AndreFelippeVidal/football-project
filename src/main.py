import click
import logfire
import logging
from utils.competitions_api import CompetitionsAPI, CompetitionsProcessor, CompetitionsDetailsProcessor
from utils.teams_api import TeamsAPI, TeamsProcessor, TeamUpcomingMatchesProcessor
from utils.matches_api import MatchesAPI, MatchesProcessor
from contracts.teams_contract import TeamsResponse
from dotenv import load_dotenv


# Configuração Logfire
logfire.configure()
logging.basicConfig(handlers=[logfire.LogfireLoggingHandler()])
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logfire.instrument_requests()
logfire.instrument_psycopg()

load_dotenv()

@click.command()
@click.option('--request_type', type=click.Choice(['teams', 'teams_upcoming_matches', 'competitions','competitions_standings','competitions_top_scorers','matches_today'], case_sensitive=False), help="Tipo de requisição a ser feita")
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
    elif request_type == 'matches_today':
        competitions_top_scorers_api = MatchesAPI(token=None)
        MatchesProcessor(competitions_top_scorers_api, schema='raw', table='matches_today').process() 
    elif request_type == 'teams_upcoming_matches':
        teams_api = TeamsAPI(token=None)
        TeamUpcomingMatchesProcessor(teams_api,schema='raw', table='teams_upcoming_matches').process()
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
    