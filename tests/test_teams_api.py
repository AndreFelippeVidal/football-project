import pytest, os
from src.utils.teams_api import TeamsAPI

@pytest.fixture
def api_instance():
    # Substitua por uma chave válida
    return TeamsAPI(token=None)

def test_get_teams(api_instance):
    teams = api_instance.get_teams(2001)  # Exemplo: ID da Champions League
    assert isinstance(teams['competition'], dict)
    assert len(teams) > 0

def test_get_team_by_id(api_instance):
    team = api_instance.get_team_by_id(64)  # Exemplo: Liverpool FC
    assert isinstance(team, dict)
    assert "name" in team
