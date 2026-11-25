"""A pretend calendar as an MCP server, serving demo/events.json.

Used in Steps 1-2. Step 3 swaps it for the real Google Calendar connector.
"""

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from party_weather.location import KIGALI
from party_weather.service import parse_iso_date

from party_demo.local_calendar import list_events as find_events

mcp = MCPServer("calendar")


@mcp.tool(
    description=(
        "List calendar events between two dates (YYYY-MM-DD), inclusive. Returns title, "
        "start, end, location and description for each event."
    )
)
def list_events(start_date: str, end_date: str) -> list[dict[str, str]]:
    try:
        start, end = parse_iso_date(start_date), parse_iso_date(end_date)
    except ValueError as error:
        raise ToolError(str(error)) from error
    return [event.to_dict() for event in find_events(start, end, KIGALI.today())]


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
