from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class CurrentSeason(BaseModel):
    id: int
    startDate: str
    endDate: str
    currentMatchday: int
    # winner: Optional[Team]

# Modelo para representar a área da competição
class Area(BaseModel):
    id: int
    name: str
    code: str
    flag: Optional[str]

# Modelo para representar a competição
class Competition(BaseModel):
    id: int
    name: str
    area: Area
    code: str
    type: str
    emblem: str
    plan: str
    current_season: CurrentSeason = Field(..., alias='currentSeason')
    number_of_available_seasons: int = Field(..., alias='numberOfAvailableSeasons')
    last_updated: str = Field(..., alias='lastUpdated')

# Modelo principal que representa a resposta da API
class CompetitionsResponse(BaseModel):
    count: int
    competitions: List[Competition]
    filters: dict
