"""Dummy celebrations for the demo, placed relative to the current week.

Run:  uv run python -m rain_check.events
It writes celebrations.ics, a calendar file to import into Outlook.
"""

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta, timezone
from pathlib import Path

KIGALI_TZ = timezone(timedelta(hours=2), "Africa/Kigali")
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
WEEK_OFFSETS = {"last": -1, "this": 0}
OUTPUT_FILE = Path(__file__).resolve().parents[2] / "celebrations.ics"


@dataclass(frozen=True)
class Celebration:
    title: str
    week: str  # "last" or "this"
    weekday: str  # "Monday" ... "Sunday"
    start: str  # "HH:MM", Kigali time
    end: str
    location: str
    setting: str  # "indoor" or "outdoor"

    def day(self, today: date) -> date:
        monday = today - timedelta(days=today.weekday())
        return monday + timedelta(weeks=WEEK_OFFSETS[self.week], days=WEEKDAYS.index(self.weekday))


CELEBRATIONS = (
    Celebration("Birthday dinner", "last", "Friday", "19:00", "22:00",
                "Restaurant in Kiyovu, Kigali", "indoor"),
    Celebration("Team BBQ", "last", "Saturday", "14:00", "18:00",
                "Nyandungu Eco-Park, Kigali", "outdoor"),
    Celebration("Office game night", "this", "Thursday", "18:00", "21:00",
                "Office lounge, Kigali", "indoor"),
    Celebration("Year-end garden party", "this", "Saturday", "15:00", "20:00",
                "Garden venue, Kacyiru, Kigali", "outdoor"),
    Celebration("Kids birthday picnic", "this", "Sunday", "11:00", "15:00",
                "Park in Nyarutarama, Kigali", "outdoor"),
)  # fmt: skip


def kigali_time(day: date, clock: str) -> datetime:
    return datetime.combine(day, time.fromisoformat(clock), KIGALI_TZ)


def ics_time(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def ics_text(value: str) -> str:
    """Escape the characters that have a meaning in .ics files."""
    return value.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")


def to_vevent(celebration: Celebration, today: date, stamp: datetime) -> list[str]:
    day = celebration.day(today)
    slug = celebration.title.lower().replace(" ", "-")
    return [
        "BEGIN:VEVENT",
        f"UID:{day:%Y%m%d}-{slug}@rain-check",  # stable: re-importing updates, not duplicates
        f"DTSTAMP:{ics_time(stamp)}",
        f"DTSTART:{ics_time(kigali_time(day, celebration.start))}",
        f"DTEND:{ics_time(kigali_time(day, celebration.end))}",
        f"SUMMARY:{ics_text(celebration.title)}",
        f"LOCATION:{ics_text(celebration.location)}",
        f"DESCRIPTION:Setting: {celebration.setting}",
        "TRANSP:TRANSPARENT",  # shows as "free", so it never blocks real meetings
        "END:VEVENT",
    ]


def build_calendar(today: date) -> str:
    stamp = datetime.now(UTC)
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//rain-check//demo//EN"]
    for celebration in CELEBRATIONS:
        lines += to_vevent(celebration, today, stamp)
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"  # the .ics format requires CRLF line endings


if __name__ == "__main__":
    today = datetime.now(KIGALI_TZ).date()
    OUTPUT_FILE.write_text(build_calendar(today), encoding="utf-8", newline="")
    for celebration in CELEBRATIONS:
        day = celebration.day(today)
        print(f"{day:%a %d %b}  {celebration.start}  {celebration.title:<24} {celebration.setting}")
    print(f"\nWrote {OUTPUT_FILE.name}: import it into Outlook.")
