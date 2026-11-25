"""Kigali weather from Open-Meteo (free, no API key)."""

import sys
from datetime import date, datetime, timedelta, timezone

import httpx

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
KIGALI = {"latitude": -1.9441, "longitude": 30.0619, "timezone": "Africa/Kigali"}
KIGALI_TZ = timezone(timedelta(hours=2))
FORECAST_DAYS = 14
PAST_DAYS = 90


def kigali_today() -> date:
    return datetime.now(KIGALI_TZ).date()


def _fetch_day(day: date, fields: str) -> dict:
    """The requested daily values for one day, e.g. {"precipitation_sum": 4.1, ...}."""
    response = httpx.get(
        FORECAST_URL,
        params={
            **KIGALI,
            "daily": fields,
            "start_date": day.isoformat(),
            "end_date": day.isoformat(),
        },
        timeout=10,
    )
    response.raise_for_status()
    return {name: values[0] for name, values in response.json()["daily"].items()}


def get_forecast(day: date) -> dict:
    """Rain probability (%), expected rain (mm) and max temperature for an upcoming day."""
    today = kigali_today()
    if not today <= day <= today + timedelta(days=FORECAST_DAYS):
        raise ValueError(
            f"{day} is not in the next {FORECAST_DAYS} days. For past dates, use get_past_weather."
        )
    values = _fetch_day(day, "precipitation_probability_max,precipitation_sum,temperature_2m_max")
    return {
        "date": day.isoformat(),
        "rain_probability_pct": values["precipitation_probability_max"],
        "rain_mm": values["precipitation_sum"],
        "max_temp_c": values["temperature_2m_max"],
    }


def get_past_weather(day: date) -> dict:
    """Rain that fell (mm) and max temperature on a past day."""
    today = kigali_today()
    if not today - timedelta(days=PAST_DAYS) <= day < today:
        raise ValueError(
            f"{day} is not in the past {PAST_DAYS} days. For today or later, use get_forecast."
        )
    values = _fetch_day(day, "precipitation_sum,temperature_2m_max")
    return {
        "date": day.isoformat(),
        "rain_mm": values["precipitation_sum"],
        "max_temp_c": values["temperature_2m_max"],
    }


if __name__ == "__main__":
    day = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else kigali_today()
    print(get_past_weather(day) if day < kigali_today() else get_forecast(day))
