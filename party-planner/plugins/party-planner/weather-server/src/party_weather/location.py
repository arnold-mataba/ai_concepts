from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone


@dataclass(frozen=True)
class Location:
    name: str
    latitude: float
    longitude: float
    timezone_name: str
    utc_offset_hours: int

    def today(self) -> date:
        return datetime.now(timezone(timedelta(hours=self.utc_offset_hours))).date()


KIGALI = Location(
    name="Kigali",
    latitude=-1.9441,
    longitude=30.0619,
    timezone_name="Africa/Kigali",
    utc_offset_hours=2,
)
