from utils.football_api import FootballAPIBase
from typing import Dict, Any


class CompetitionsAPI(FootballAPIBase):
    def get_competitions(self, plan: str = "TIER_ONE") -> Dict[str, Any]:
        """
        Retorna todas as competições disponíveis.
        :param plan: Nível da competição (ex.: TIER_ONE, TIER_TWO)
        """
        return self._make_request("competitions", params={"plan": plan})

    def get_competition_by_id(self, competition_id: int) -> Dict[str, Any]:
        """
        Retorna detalhes de uma competição específica.
        """
        return self._make_request(f"competitions/{competition_id}")

    def get_matches(self, competition_id: int) -> Dict[str, Any]:
        """
        Retorna as partidas de uma competição específica.
        """
        return self._make_paginated_request(f"competitions/{competition_id}/matches")
