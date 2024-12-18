from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


# Modelo para representar a área de um time
class Area(BaseModel):
    id: int
    name: str
    code: str
    flag: Optional[str]


# Modelo para representar as competições em que um time está participando
class RunningCompetition(BaseModel):
    id: int
    name: str
    code: str
    type: str
    emblem: Optional[str]


# Modelo para representar o contrato do técnico
class Contract(BaseModel):
    start: Optional[str]
    until: Optional[str]


# Modelo para representar o técnico do time
class Coach(BaseModel):
    id: Optional[int]
    first_name: Optional[str] = Field(..., alias='firstName')
    last_name: Optional[str] = Field(..., alias='lastName')
    name: Optional[str]
    date_of_birth: Optional[date] = Field(..., alias='dateOfBirth')
    nationality: Optional[str]
    contract: Optional[Contract]


# Modelo para representar os jogadores do time
class SquadMember(BaseModel):
    id: int
    name: str
    position: Optional[str]
    date_of_birth: Optional[date] = Field(..., alias='dateOfBirth')
    nationality: Optional[str]


# Modelo para representar os times
class Team(BaseModel):
    area: Optional[Area] = None
    id: int
    name: str
    short_name: str = Field(..., alias='shortName')
    tla: str
    crest: str
    address: str = None
    website: Optional[str] = None
    founded: Optional[int] = None
    club_colors: Optional[str] = Field(None, alias='clubColors')
    venue: Optional[str] = None
    running_competitions: Optional[List[RunningCompetition]] = Field(None, alias='runningCompetitions')
    coach: Optional[Coach] = None
    squad: Optional[List[SquadMember]] = None
    staff: Optional[List[dict]] = None # Adicione um modelo específico para staff, se necessário
    last_updated: Optional[datetime] = Field(None, alias='lastUpdated')

# Modelo para a competição
class Competition(BaseModel):
    id: int
    name: str
    code: str
    type: str
    emblem: Optional[str]


# Modelo para a temporada
class Season(BaseModel):
    id: int
    start_date: date = Field(..., alias='startDate')
    end_date: date = Field(..., alias='endDate')
    current_matchday: Optional[int] = Field(..., alias='currentMatchday')
    winner: Optional[Team]  # Ajuste caso winner tenha uma estrutura mais complexa


# Modelo principal que representa a resposta da API
class TeamsResponse(BaseModel):
    count: int
    filters: dict
    competition: Competition
    season: Season
    teams: List[Team]
