"""Kigali weather from Open-Meteo (free, no API key)."""

import sys
from datetime import date, datetime, time, timedelta, timezone

import httpx

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
KIGALI: dict[str, float | str] = {
    "latitude": -1.9441,
    "longitude": 30.0619,
    "timezone": "Africa/Kigali",
}
KIGALI_TZ = timezone(timedelta(hours=2))
FORECAST_DAYS = 14
PAST_DAYS = 90


def kigali_today() -> date:
    return datetime.now(KIGALI_TZ).date()


def _fetch(day: date, daily: str, hourly: str) -> dict:
    """Open-Meteo's daily and hourly values for one day, as returned by the API."""
    response = httpx.get(
        FORECAST_URL,
        params={
            **KIGALI,
            "daily": daily,
            "hourly": hourly,
            "start_date": day.isoformat(),
            "end_date": day.isoformat(),
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def _event_rain(hourly: dict, start: time | None, end: time | None) -> dict:
    """Rain during the event's hours. Empty when no hours are given.

    Each hourly value covers the hour *before* its timestamp, so 14:00-18:00
    uses the values stamped 15:00, 16:00, 17:00 and 18:00.
    """
    if start is None or end is None:
        return {}
    if end <= start:
        raise ValueError(f"end_time {end:%H:%M} must be after start_time {start:%H:%M}.")

    hours = [
        index
        for index, stamp in enumerate(hourly["time"])
        if start < datetime.fromisoformat(stamp).time() <= end
    ]
    rain = [hourly["precipitation"][index] or 0.0 for index in hours]
    result = {"event_hours": f"{start:%H:%M}-{end:%H:%M}", "event_rain_mm": round(sum(rain), 1)}
    if "precipitation_probability" in hourly:
        chances = [hourly["precipitation_probability"][index] or 0 for index in hours]
        result["event_rain_probability_pct"] = max(chances, default=0)
    return result


def get_forecast(day: date, start: time | None = None, end: time | None = None) -> dict:
    """Forecast for an upcoming day; with start/end, also the rain during those hours."""
    today = kigali_today()
    if not today <= day <= today + timedelta(days=FORECAST_DAYS):
        raise ValueError(
            f"{day} is not in the next {FORECAST_DAYS} days. For past dates, use get_past_weather."
        )
    data = _fetch(
        day,
        daily="precipitation_probability_max,precipitation_sum,temperature_2m_max",
        hourly="precipitation,precipitation_probability",
    )
    daily = data["daily"]
    return {
        "date": day.isoformat(),
        "rain_probability_pct": daily["precipitation_probability_max"][0],
        "rain_mm": daily["precipitation_sum"][0],
        "max_temp_c": daily["temperature_2m_max"][0],
        **_event_rain(data["hourly"], start, end),
    }


def get_past_weather(day: date, start: time | None = None, end: time | None = None) -> dict:
    """Observed weather for a past day; with start/end, also the rain during those hours."""
    today = kigali_today()
    if not today - timedelta(days=PAST_DAYS) <= day < today:
        raise ValueError(
            f"{day} is not in the past {PAST_DAYS} days. For today or later, use get_forecast."
        )
    data = _fetch(day, daily="precipitation_sum,temperature_2m_max", hourly="precipitation")
    daily = data["daily"]
    return {
        "date": day.isoformat(),
        "rain_mm": daily["precipitation_sum"][0],
        "max_temp_c": daily["temperature_2m_max"][0],
        **_event_rain(data["hourly"], start, end),
    }


if __name__ == "__main__":
    # python -m rain_check.weather 2026-11-21 [14:00 18:00]
    args = sys.argv[1:]
    day = date.fromisoformat(args[0]) if args else kigali_today()
    hours = [time.fromisoformat(arg) for arg in args[1:3]]
    start, end = hours if len(hours) == 2 else (None, None)
    lookup = get_past_weather if day < kigali_today() else get_forecast
    print(lookup(day, start, end))
