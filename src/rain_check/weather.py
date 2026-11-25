"""Kigali weather from Open-Meteo (free, no API key)."""

import sys
from datetime import date

import httpx

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
KIGALI = {"latitude": -1.9441, "longitude": 30.0619, "timezone": "Africa/Kigali"}
DAILY_FIELDS = "precipitation_probability_max,precipitation_sum,temperature_2m_max"


def get_forecast(day: date) -> dict:
    """Rain probability (%), expected rain (mm) and max temperature for one day in Kigali."""
    response = httpx.get(
        FORECAST_URL,
        params={
            **KIGALI,
            "daily": DAILY_FIELDS,
            "start_date": day.isoformat(),
            "end_date": day.isoformat(),
        },
        timeout=10,
    )
    response.raise_for_status()
    daily = response.json()["daily"]
    return {
        "date": day.isoformat(),
        "rain_probability_pct": daily["precipitation_probability_max"][0],
        "rain_mm": daily["precipitation_sum"][0],
        "max_temp_c": daily["temperature_2m_max"][0],
    }


if __name__ == "__main__":
    day = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    print(get_forecast(day))
