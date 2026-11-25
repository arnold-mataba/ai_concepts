"""Step 1a: a tool is just a name, a description, an input schema and a function.

Lists every tool exactly as an AI app receives it, then calls one directly, with no AI involved.

Run:  uv run party-tools
"""

import asyncio
import json
from datetime import date, timedelta
from typing import Any

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from party_weather.location import KIGALI

from party_demo.paths import PROJECT_ROOT, STEP1_MCP_CONFIG

SATURDAY = 5


def load_servers() -> dict[str, StdioServerParameters]:
    config = json.loads(STEP1_MCP_CONFIG.read_text(encoding="utf-8"))
    return {
        name: StdioServerParameters(command=spec["command"], args=spec["args"], cwd=PROJECT_ROOT)
        for name, spec in config["mcpServers"].items()
    }


def next_saturday(today: date) -> date:
    return today + timedelta(days=(SATURDAY - today.weekday()) % 7)


async def call_tool(
    params: StdioServerParameters, name: str | None = None, arguments: dict[str, Any] | None = None
) -> Any:
    """List the server's tools, or call one of them when `name` is given."""
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        if name is None:
            return (await session.list_tools()).tools
        return await session.call_tool(name, arguments or {})


async def run() -> None:
    servers = load_servers()

    for server, params in servers.items():
        for tool in await call_tool(params):
            print(f"\n■ {server} → {tool.name}\n  {tool.description}")
            print("  input_schema:", json.dumps(tool.input_schema, indent=2).replace("\n", "\n  "))

    arguments = {"date": next_saturday(KIGALI.today()).isoformat()}
    print(f"\n── Calling get_forecast({arguments}) directly. No AI involved. ──")
    result = await call_tool(servers["weather"], "get_forecast", arguments)
    print(result.content[0].text)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
