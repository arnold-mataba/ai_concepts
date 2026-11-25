"""A pretend calendar read from demo/events.json.

Dates are stored relative to the current week ("last"/"this" + weekday), so the demo
never goes stale. Step 3 replaces this file with the real Google Calendar connector.
"""

import json
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path

EVENTS_FILE = Path(__file__).resolve().parents[2] / "demo" / "events.json"
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
WEEK_OFFSETS = {"last": -1, "this": 0}


@dataclass(frozen=True)
class Event:
    title: str
    start: datetime
    end: datetime
    location: str
    setting: str

    def to_dict(self) -> dict[str, str]:
        return {
            "title": self.title,
            "start": self.start.isoformat(timespec="minutes"),
            "end": self.end.isoformat(timespec="minutes"),
            "location": self.location,
            "description": f"Setting: {self.setting}",
        }


def resolve_day(week: str, weekday: str, today: date) -> date:
    monday = today - timedelta(days=today.weekday())
    return monday + timedelta(weeks=WEEK_OFFSETS[week], days=WEEKDAYS.index(weekday))


def load_events(today: date, path: Path = EVENTS_FILE) -> list[Event]:
    events = []
    for raw in json.loads(path.read_text(encoding="utf-8")):
        day = resolve_day(raw["week"], raw["weekday"], today)
        events.append(
            Event(
                title=raw["title"],
                start=datetime.combine(day, time.fromisoformat(raw["start"])),
                end=datetime.combine(day, time.fromisoformat(raw["end"])),
                location=raw["location"],
                setting=raw["setting"],
            )
        )
    return sorted(events, key=lambda event: event.start)


def list_events(start: date, end: date, today: date) -> list[Event]:
    return [event for event in load_events(today) if start <= event.start.date() <= end]
