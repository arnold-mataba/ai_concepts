"""MCP server: exposes the weather functions as tools that any MCP app can call."""

import datetime
from collections.abc import Callable

import httpx
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from rain_check import weather

mcp = MCPServer("weather")

Lookup = Callable[[datetime.date, datetime.time | None, datetime.time | None], dict]


def _parse_time(value: str | None) -> datetime.time | None:
    return datetime.time.fromisoformat(value) if value else None


def _lookup(fetch: Lookup, date: str, start_time: str | None, end_time: str | None) -> dict:
    """Run a weather lookup. Expected failures become a ToolError, so Claude can read the reason."""
    try:
        day = datetime.date.fromisoformat(date)
        return fetch(day, _parse_time(start_time), _parse_time(end_time))
    except ValueError as error:
        raise ToolError(str(error)) from error
    except httpx.HTTPError as error:
        raise ToolError(
            f"The weather service is unavailable right now ({error}). Try again in a minute."
        ) from error


@mcp.tool()
def get_forecast(date: str, start_time: str | None = None, end_time: str | None = None) -> dict:
    """Weather forecast for one upcoming day in Kigali, today up to 14 days ahead.

    Returns rain probability (%), expected rain (mm) and max temperature (°C) for the day.
    With start_time and end_time, also returns the rain expected during those hours.

    Args:
        date: The day to check, as YYYY-MM-DD.
        start_time: Optional event start, Kigali time, as HH:MM.
        end_time: Optional event end, Kigali time, as HH:MM.
    """
    return _lookup(weather.get_forecast, date, start_time, end_time)


@mcp.tool()
def get_past_weather(date: str, start_time: str | None = None, end_time: str | None = None) -> dict:
    """Observed weather for one past day in Kigali, up to 90 days back.

    Returns the rain that fell (mm) and max temperature (°C) for the day.
    With start_time and end_time, also returns the rain that fell during those hours.

    Args:
        date: The day to check, as YYYY-MM-DD.
        start_time: Optional event start, Kigali time, as HH:MM.
        end_time: Optional event end, Kigali time, as HH:MM.
    """
    return _lookup(weather.get_past_weather, date, start_time, end_time)


def main() -> None:
    mcp.run()
