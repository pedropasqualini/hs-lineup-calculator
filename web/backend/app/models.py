"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class CrawlerOptions(BaseModel):
    """Options for the HSReplay crawler."""
    league_rank_range: str = "BRONZE_THROUGH_GOLD"
    game_type: str = "RANKED_STANDARD"
    region: str = "ALL"
    time_range: str = "LAST_7_DAYS"
    min_games: int = Field(default=10000, ge=1000, le=100000)


class MatchupEntry(BaseModel):
    """Single matchup entry for editing."""
    row_deck: str
    col_deck: str
    value: float = Field(ge=0, le=100)


class MatchupMatrix(BaseModel):
    """Complete matchup matrix."""
    deck_names: list[str]
    values: list[list[float]]  # 2D matrix of matchup percentages


class FieldEntry(BaseModel):
    """Single field entry."""
    deck: str
    pct: float = Field(ge=0)


class FieldData(BaseModel):
    """Complete field data."""
    entries: list[FieldEntry]


class CalculateRequest(BaseModel):
    """Request to calculate optimal lineups."""
    matchups: MatchupMatrix
    field: FieldData


class LineupResult(BaseModel):
    """Single lineup result."""
    decks: list[str]
    win_rate: float


class CalculationStatus(BaseModel):
    """Status update for calculation progress."""
    phase: str  # "field_generation", "lineup_calculation"
    progress: float  # 0.0 to 1.0
    message: str
    completed: bool = False
    results: Optional[list[LineupResult]] = None


class CrawlerStatus(BaseModel):
    """Status update for crawler progress."""
    phase: str  # "fetching_matchups", "fetching_archetypes", "processing"
    progress: float
    message: str
    completed: bool = False
    matchups: Optional[MatchupMatrix] = None
    field: Optional[FieldData] = None
    error: Optional[str] = None
