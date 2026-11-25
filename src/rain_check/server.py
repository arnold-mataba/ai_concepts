"""MCP server: exposes the weather function as a tool that any MCP app can call."""

import datetime

from mcp.server.mcpserver import MCPServer

from rain_check import weather

mcp = MCPServer("weather")


@mcp.tool()
def get_forecast(date: str) -> dict:
    """Weather forecast for one day in Kigali, today up to 14 days ahead.

    Returns rain probability (%), expected rain (mm) and max temperature (°C).

    Args:
        date: The day to check, as YYYY-MM-DD.
    """
    return weather.get_forecast(datetime.date.fromisoformat(date))


def main() -> None:
    mcp.run()
