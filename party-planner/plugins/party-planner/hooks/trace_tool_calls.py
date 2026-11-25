# /// script
# requires-python = ">=3.11"
# ///
"""Claude Code PreToolUse hook: append every tool call to tool_trace.log in the project folder.

The prefix of a tool's name tells you which layer it came from, so the log labels each call.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

LOG_NAME = "tool_trace.log"
MAX_INPUT_CHARS = 140


def classify(tool_name: str) -> str:
    if tool_name.startswith("mcp__claude_ai_"):
        return "connector"
    if tool_name.startswith("mcp__plugin_"):
        return "plugin MCP"
    if tool_name.startswith("mcp__"):
        return "MCP server"
    if tool_name == "Skill":
        return "skill"
    return "built-in"


def format_line(event: dict) -> str:
    name = event.get("tool_name", "?")
    tool_input = json.dumps(event.get("tool_input", {}), ensure_ascii=False)
    if len(tool_input) > MAX_INPUT_CHARS:
        tool_input = tool_input[: MAX_INPUT_CHARS - 1] + "…"
    return f"{datetime.now():%H:%M:%S}  {classify(name):<11} {name:<55} {tool_input}"


def main() -> int:
    event = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
    log_path = Path(event.get("cwd") or ".") / LOG_NAME
    with log_path.open("a", encoding="utf-8") as log:
        log.write(format_line(event) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
