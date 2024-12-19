from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, date
from contracts.competitions_standings_contract import Season
from contracts.teams_contract import Team

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
    emblem: Optional[str]

# Modelo para representar o placar de uma partida
class ScoreDetails(BaseModel):
    home: Optional[int]
    away: Optional[int]

class Score(BaseModel):
    winner: Optional[str]
    duration: str
    full_time: ScoreDetails = Field(..., alias='fullTime')
    half_time: ScoreDetails = Field(..., alias='halfTime')

# Modelo para representar os árbitros
class Referee(BaseModel):
    id: int
    name: str
    type: str
    nationality: Optional[str]

# Modelo para representar uma partida
class Match(BaseModel):
    area: Area
    competition: Competition
    season: Season
    id: int
    utc_date: datetime = Field(..., alias='utcDate')
    status: str
    matchday: Optional[int]
    stage: str
    which_group: Optional[str] = Field(..., alias='group')
    last_updated: datetime = Field(..., alias='lastUpdated')
    home_team: Team = Field(..., alias='homeTeam')
    away_team: Team = Field(..., alias='awayTeam')
    score: Score
    odds: Optional[Dict[str, str]]
    referees: List[Referee]

class ResultSet(BaseModel):
    count: int
    competitions: str
    first: date
    last: date
    played: int
    wins: int = None
    draws: int = None
    losses: int = None

class Filters(BaseModel):
    date_from: date = Field(None, alias='dateFrom')
    date_to: date = Field(None, alias='dateTo')
    permission: str = None
    competitions: str = None
    permission: str =  None
    status: List[str] = None
    limit: int = None

# Modelo principal que representa a resposta da API
class MatchesTodayResponse(BaseModel):
    filters: Filters#Dict[str, str]
    result_set: ResultSet = Field(..., alias='resultSet')
    matches: List[Match]
