import pytest
from unittest.mock import patch
from src.utils.competitions_api import CompetitionsAPI
from tests.fixtures.mock_responses import mock_competitions_response

@pytest.fixture
def api_instance():
    # Substitua por uma chave válida
    return CompetitionsAPI(token=None)

def test_get_competition_by_id(api_instance):
    competition = api_instance.get_competition_by_id(2001)  # Exemplo: Champions League
    assert isinstance(competition, dict)
    assert "name" in competition


@patch('src.utils.football_api.requests.get')  # Patch na função requests.get usada na CompetitionsAPI
def test_get_competitions(mock_get, mock_competitions_response, api_instance):
    # Simulando a resposta da API com os dados mockados
    mock_get.return_value.json.return_value = mock_competitions_response
    mock_get.return_value.status_code = 200

    competitions = api_instance.get_competitions()
    assert isinstance(competitions['competitions'], list)
    assert len(competitions['competitions']) > 0
    assert competitions['competitions'][0]['name'] == 'Champions League'

# def test_get_competitions(api_instance):
#     competitions = api_instance.get_competitions()
#     print(competitions)
#     assert isinstance(competitions['competitions'], list)
#     assert len(competitions) > 0