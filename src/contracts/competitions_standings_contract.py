from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from contracts.teams_contract import Team  # Reutilizando o contrato Team

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
    code: str
    type: str
    emblem: str

# Modelo para representar a temporada
class Season(BaseModel):
    id: int
    start_date: date = Field(..., alias="startDate")
    end_date: date = Field(..., alias="endDate")
    current_matchday: Optional[int] = Field(None, alias="currentMatchday")
    winner: Optional[Team]

# Modelo para representar um time na tabela
class TeamStanding(BaseModel):
    id: int
    name: str
    short_name: str = Field(..., alias="shortName")
    tla: str
    crest: Optional[str]

# Modelo para representar uma entrada na tabela de classificação
class StandingTableEntry(BaseModel):
    position: int
    team: TeamStanding
    played_games: int = Field(..., alias="playedGames")
    form: Optional[str]
    won: int
    draw: int
    lost: int
    points: int
    goals_for: int = Field(..., alias="goalsFor")
    goals_against: int = Field(..., alias="goalsAgainst")
    goal_difference: int = Field(..., alias="goalDifference")

# Modelo para representar um agrupamento de classificação
class Standing(BaseModel):
    stage: str
    type: str
    group: Optional[str]
    table: List[StandingTableEntry]

# Modelo principal que representa a resposta do endpoint de standings
class CompetitionStandingsResponse(BaseModel):
    filters: dict
    area: Area
    competition: Competition
    season: Season
    standings: List[Standing]
