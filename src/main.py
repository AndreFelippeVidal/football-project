import click
from utils.competitions_api import CompetitionsAPI
from utils.teams_api import TeamsAPI

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
        print(competitions_api.get_competitions())
    else:
        print("Tipo de requisição inválido!")

if __name__ == '__main__':
    main()