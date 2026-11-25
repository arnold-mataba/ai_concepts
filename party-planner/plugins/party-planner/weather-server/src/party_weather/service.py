"""Weather rules shared by every layer of the demo (raw tools, MCP server, connector)."""

import os
from collections.abc import Callable
from datetime import date, timedelta
from typing import Protocol

from party_weather.location import KIGALI, Location
from party_weather.models import DailyWeather
from party_weather.open_meteo import OpenMeteoClient

MAX_FORECAST_DAYS = 14
MAX_PAST_DAYS = 90
SIMULATE_RAIN_ENV = "PARTY_SIMULATE_RAIN"

FORECAST_DESCRIPTION = (
    f"Weather forecast for one upcoming date in Kigali (today up to {MAX_FORECAST_DAYS} days "
    "ahead). Returns a summary, rain probability (%), expected rain (mm) and max temperature."
)
PAST_WEATHER_DESCRIPTION = (
    f"Observed weather for one past date in Kigali (up to {MAX_PAST_DAYS} days back). "
    "Returns a summary, rain that fell (mm) and max temperature."
)


class WeatherProvider(Protocol):
    def daily(self, day: date) -> DailyWeather: ...


class DateOutOfRangeError(ValueError):
    pass


class WeatherService:
    def __init__(
        self,
        provider: WeatherProvider,
        location: Location = KIGALI,
        simulate_rain: bool = False,
        today: Callable[[], date] | None = None,
    ) -> None:
        self._provider = provider
        self._simulate_rain = simulate_rain
        self._today = today or location.today

    def forecast(self, day: date) -> DailyWeather:
        today = self._today()
        last_day = today + timedelta(days=MAX_FORECAST_DAYS)
        if not today <= day <= last_day:
            raise DateOutOfRangeError(
                f"{day} is outside the forecast window ({today} to {last_day}). "
                "Use get_past_weather for past dates."
            )
        weather = self._provider.daily(day)
        return weather.with_simulated_rain() if self._simulate_rain else weather

    def past_weather(self, day: date) -> DailyWeather:
        today = self._today()
        first_day = today - timedelta(days=MAX_PAST_DAYS)
        if not first_day <= day < today:
            raise DateOutOfRangeError(
                f"{day} is not a past date in range ({first_day} to yesterday). "
                "Use get_forecast for today or later."
            )
        return self._provider.daily(day).without_probability()


def parse_iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"Expected a date like 2026-11-28, got {value!r}.") from error


def build_service() -> WeatherService:
    simulate_rain = os.environ.get(SIMULATE_RAIN_ENV, "0") == "1"
    return WeatherService(OpenMeteoClient(KIGALI), KIGALI, simulate_rain=simulate_rain)
