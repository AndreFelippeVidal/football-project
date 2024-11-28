import pytest

@pytest.fixture
def mock_competitions_response():
    return {
        "count": 2,
        "competitions": [
            {"id": 2001, "name": "Champions League"},
            {"id": 2021, "name": "Premier League"},
        ]
    }

@pytest.fixture
def mock_team_response():
    return {
        "id": 64,
        "name": "Liverpool FC",
        "area": {"name": "England"}
    }
