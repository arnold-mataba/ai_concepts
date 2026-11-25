"""Step 1b: watch Claude invoke tools, one request and one result at a time.

Runs Claude Code headless (your normal Claude Code login, no API key) with only our two
MCP servers and no built-in tools, and prints each `tool_use` / `tool_result` pair.
Each result carries the `tool_use_id` of the request it answers.

Run:  uv run party-watch                     readable view
      uv run party-watch --raw               the raw JSON blocks as well
      uv run party-watch "your own question"
"""

import argparse
import json
import shutil
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from party_demo.paths import PROJECT_ROOT, STEP1_MCP_CONFIG

DEFAULT_QUESTION = (
    "Which of my celebrations last week and this week were, or will be, affected by rain?"
)
ALLOWED_TOOLS = (
    "mcp__calendar__list_events",
    "mcp__weather__get_forecast",
    "mcp__weather__get_past_weather",
)
MAX_SHOWN_CHARS = 300
RULE = "─" * 72


def find_claude() -> str:
    """Claude Code on PATH, otherwise the copy bundled with the VS Code extension."""
    if on_path := shutil.which("claude"):
        return on_path
    pattern = ".vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude*"
    bundled = [path for path in Path.home().glob(pattern) if path.suffix in ("", ".exe")]
    if not bundled:
        sys.exit("Claude Code CLI not found. Install it, or add it to PATH.")
    return str(max(bundled, key=lambda path: path.stat().st_mtime))


def build_command(claude: str, question: str) -> list[str]:
    return [
        claude,
        "-p",
        question,
        "--output-format", "stream-json",
        "--verbose",
        "--mcp-config", str(STEP1_MCP_CONFIG),
        "--strict-mcp-config",            # only our servers
        "--tools", "",                    # no built-in tools (Read, Bash, ...)
        "--allowedTools", ",".join(ALLOWED_TOOLS),
        "--no-session-persistence",
    ]  # fmt: skip


def stream_events(command: list[str]) -> Iterator[dict[str, Any]]:
    with subprocess.Popen(
        command, cwd=PROJECT_ROOT, stdout=subprocess.PIPE, text=True, encoding="utf-8"
    ) as process:
        assert process.stdout is not None
        for line in process.stdout:
            if line.strip():
                yield json.loads(line)


def _short(text: str) -> str:
    return text if len(text) <= MAX_SHOWN_CHARS else text[:MAX_SHOWN_CHARS] + " …"


def _result_text(content: str | list[dict[str, Any]]) -> str:
    if isinstance(content, str):
        return content
    return " ".join(part.get("text", "") for part in content)


def describe(event: dict[str, Any], raw: bool = False) -> list[str]:
    """Turn one stream-json event into the lines we print. Unknown events print nothing."""
    kind = event.get("type")
    if kind == "system" and event.get("subtype") == "init":
        return [f"Claude was given these tools: {', '.join(event.get('tools', []))}"]
    if kind == "result":
        return [f"{RULE}\ndone: {event.get('num_turns')} turns"]

    lines = []
    for block in event.get("message", {}).get("content", []):
        block_type = block.get("type")
        if kind == "assistant" and block_type == "tool_use":
            arguments = json.dumps(block["input"], ensure_ascii=False)
            lines.append(f"\n→ tool_use     id={block['id']}\n  {block['name']}({arguments})")
        elif kind == "user" and block_type == "tool_result":
            status = "ERROR  " if block.get("is_error") else ""
            text = _short(_result_text(block.get("content", "")))
            lines.append(f"← tool_result  tool_use_id={block['tool_use_id']}\n  {status}{text}")
        elif kind == "assistant" and block_type == "text":
            lines.append(f"\nClaude: {block['text']}")
        else:
            continue
        if raw:
            lines.append("  raw: " + json.dumps(block, ensure_ascii=False))
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Watch Claude invoke tools")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    parser.add_argument("--raw", action="store_true", help="also print the raw JSON blocks")
    args = parser.parse_args()

    print(f"{RULE}\nYOU: {args.question}\n{RULE}")
    for event in stream_events(build_command(find_claude(), args.question)):
        for line in describe(event, raw=args.raw):
            print(line)


if __name__ == "__main__":
    main()
