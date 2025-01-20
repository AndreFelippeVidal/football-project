from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime, date
from contracts.teams_contract import Team


# Modelo para representar a área da competição
class Area(BaseModel):
    id: int
    name: str
    code: str
    flag: Optional[str]

class CurrentSeason(BaseModel):
    id: int
    start_date: date = Field(..., alias='startDate')
    end_date: date = Field(..., alias='endDate')
    current_matchday: Optional[int] = Field(None, alias='currentMatchday')
    winner: Optional[Team]

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
    last_updated: datetime = Field(..., alias='lastUpdated')

# Modelo principal que representa a resposta da API
class CompetitionsResponse(BaseModel):
    count: int
    competitions: List[Competition]
    filters: dict

