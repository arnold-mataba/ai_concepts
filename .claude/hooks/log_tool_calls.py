# /// script
# requires-python = ">=3.12"
# ///
"""Claude Code hook: before every tool call, append one line to tool_calls.log.

The start of a tool's name tells which layer it comes from, so each line gets a label.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

LOG_FILE = "tool_calls.log"


def layer(tool_name: str) -> str:
    if tool_name.startswith("mcp__claude_ai_"):
        return "connector"
    if tool_name.startswith("mcp__"):
        return "MCP server"
    if tool_name == "Skill":
        return "skill"
    return "built-in"


def main() -> None:
    event = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
    name = event["tool_name"]
    arguments = json.dumps(event.get("tool_input", {}), ensure_ascii=False)
    line = f"{datetime.now():%H:%M:%S}  {layer(name):<10}  {name}  {arguments}\n"
    with (Path(event["cwd"]) / LOG_FILE).open("a", encoding="utf-8") as log:
        log.write(line)


if __name__ == "__main__":
    main()
