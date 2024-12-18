from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date, datetime
from contracts.teams_contract import Team 
from contracts.competitions_standings_contract import Season

class Player(BaseModel):
    id: int
    name: str
    first_name: Optional[str] = Field(..., alias="firstName")
    last_name: Optional[str] = Field(..., alias="lastName")
    date_of_birth: Optional[date] = Field(..., alias="dateOfBirth")
    nationality: Optional[str]
    section: Optional[str]
    position: Optional[str]
    shirt_number: Optional[int] = Field(..., alias="shirtNumber")
    last_updated: datetime = Field(..., alias="lastUpdated")

class Scorer(BaseModel):
    player: Player
    team: Optional[Team]
    played_matches: int = Field(..., alias="playedMatches")
    goals: int
    assists: Optional[int]
    penalties: Optional[int]

class Competition(BaseModel):
    id: int
    name: str
    code: str
    type: str
    emblem: str

class TopScorersResponse(BaseModel):
    count: int
    filters: dict
    competition: Competition
    season: Season
    scorers: List[Scorer]
