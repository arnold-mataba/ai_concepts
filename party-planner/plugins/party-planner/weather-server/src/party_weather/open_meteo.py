"""Thin client for the free Open-Meteo API (no API key needed)."""

from datetime import date
from typing import Any

import httpx

from party_weather.location import Location
from party_weather.models import DailyWeather

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
DAILY_FIELDS = "weather_code,temperature_2m_max,precipitation_sum,precipitation_probability_max"

# WMO weather interpretation codes, grouped into ranges.
_WEATHER_CODE_RANGES = (
    (0, 0, "Clear sky"),
    (1, 3, "Partly cloudy"),
    (45, 48, "Fog"),
    (51, 57, "Drizzle"),
    (61, 67, "Rain"),
    (71, 77, "Snow"),
    (80, 82, "Rain showers"),
    (95, 99, "Thunderstorm"),
)


def describe_weather_code(code: int | None) -> str:
    if code is not None:
        for low, high, label in _WEATHER_CODE_RANGES:
            if low <= code <= high:
                return label
    return "Unknown"


def parse_daily(payload: dict[str, Any]) -> DailyWeather:
    daily = payload["daily"]

    def first(field: str) -> Any:
        return (daily.get(field) or [None])[0]

    probability = first("precipitation_probability_max")
    return DailyWeather(
        day=date.fromisoformat(first("time")),
        summary=describe_weather_code(first("weather_code")),
        rain_mm=float(first("precipitation_sum") or 0.0),
        rain_probability_pct=None if probability is None else int(probability),
        max_temp_c=first("temperature_2m_max"),
    )


class OpenMeteoClient:
    def __init__(self, location: Location, http: httpx.Client | None = None) -> None:
        self._location = location
        self._http = http or httpx.Client(timeout=10.0)

    def daily(self, day: date) -> DailyWeather:
        response = self._http.get(
            FORECAST_URL,
            params={
                "latitude": self._location.latitude,
                "longitude": self._location.longitude,
                "timezone": self._location.timezone_name,
                "daily": DAILY_FIELDS,
                "start_date": day.isoformat(),
                "end_date": day.isoformat(),
            },
        )
        response.raise_for_status()
        return parse_daily(response.json())
