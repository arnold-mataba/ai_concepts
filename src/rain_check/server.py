"""MCP server: exposes the weather functions as tools that any MCP app can call."""

import datetime
from collections.abc import Callable

import httpx
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from rain_check import weather

mcp = MCPServer("weather")


def _lookup(fetch: Callable[[datetime.date], dict], date: str) -> dict:
    """Run a weather lookup. Expected failures become a ToolError, so Claude can read the reason."""
    try:
        return fetch(datetime.date.fromisoformat(date))
    except ValueError as error:
        raise ToolError(str(error)) from error
    except httpx.HTTPError as error:
        raise ToolError(
            f"The weather service is unavailable right now ({error}). Try again in a minute."
        ) from error


@mcp.tool()
def get_forecast(date: str) -> dict:
    """Weather forecast for one upcoming day in Kigali, today up to 14 days ahead.

    Returns rain probability (%), expected rain (mm) and max temperature (°C).

    Args:
        date: The day to check, as YYYY-MM-DD.
    """
    return _lookup(weather.get_forecast, date)


@mcp.tool()
def get_past_weather(date: str) -> dict:
    """Observed weather for one past day in Kigali, up to 90 days back.

    Returns the rain that fell (mm) and max temperature (°C).

    Args:
        date: The day to check, as YYYY-MM-DD.
    """
    return _lookup(weather.get_past_weather, date)


def main() -> None:
    mcp.run()
