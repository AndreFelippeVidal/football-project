from utils.football_api import FootballAPIBase
from typing import Dict, Any


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
