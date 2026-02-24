from dataclasses import dataclass
from datetime import datetime


@dataclass
class NormalizedOutcome:
    name: str
    odds: float


@dataclass
class NormalizedEvent:
    sport: str
    league: str
    teams: list[str]
    start_time: datetime
    bookmaker: str
    outcomes: list[NormalizedOutcome]
