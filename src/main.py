from utils.competitions_api import CompetitionsAPI
from utils.teams_api import TeamsAPI

if __name__ == "__main__":
    # Substitua "SUA_CHAVE" pela sua chave gerada no site da API
    token = None

    # Testando CompetitionsAPI
    competitions_api = CompetitionsAPI(token=token)
    print("Competições Disponíveis:")
    print(competitions_api.get_competitions())

    print("\nDetalhes de uma Competição:")
    print(competitions_api.get_competition_by_id(2001))  # Exemplo: ID da Champions League

    # Testando TeamsAPI
    teams_api = TeamsAPI(token=token)
    print("\nTimes de uma Competição:")
    print(teams_api.get_teams(2001))  # Exemplo: Times da Champions League

    print("\nDetalhes de um Time:")
    print(teams_api.get_team_by_id(64))  # Exemplo: ID do Liverpool
