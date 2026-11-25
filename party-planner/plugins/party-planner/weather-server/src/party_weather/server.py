"""MCP server: the same weather functions, now usable by any MCP client.

stdio (default)  -> Claude Code / Claude Desktop start it as a local process.
--http           -> served over HTTP, so it can be added to claude.ai as a custom connector.
"""

import argparse
from collections.abc import Callable

import httpx
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from party_weather.models import DailyWeather
from party_weather.service import (
    FORECAST_DESCRIPTION,
    PAST_WEATHER_DESCRIPTION,
    build_service,
    parse_iso_date,
)

mcp = MCPServer("weather")
_service = build_service()


def _respond(lookup: Callable[[], DailyWeather]) -> dict[str, object]:
    """Turn expected failures into ToolError so Claude sees the reason and can correct itself."""
    try:
        return lookup().to_dict()
    except ValueError as error:
        raise ToolError(str(error)) from error
    except httpx.HTTPError as error:
        raise ToolError(
            "The weather service is unavailable right now. Try again shortly."
        ) from error


@mcp.tool(description=FORECAST_DESCRIPTION)
def get_forecast(date: str) -> dict[str, object]:
    return _respond(lambda: _service.forecast(parse_iso_date(date)))


@mcp.tool(description=PAST_WEATHER_DESCRIPTION)
def get_past_weather(date: str) -> dict[str, object]:
    return _respond(lambda: _service.past_weather(parse_iso_date(date)))


def main() -> None:
    parser = argparse.ArgumentParser(description="Kigali weather MCP server")
    parser.add_argument("--http", action="store_true", help="serve over HTTP instead of stdio")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.http:
        # 0.0.0.0 so a tunnel (ngrok / cloudflared) can reach it. Demo only.
        mcp.run(transport="streamable-http", host="0.0.0.0", port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
