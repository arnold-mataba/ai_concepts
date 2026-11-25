from datetime import date

from party_demo.inspect_tools import next_saturday
from party_demo.watch_tool_calls import build_command, describe


def test_tool_use_and_result_share_an_id():
    tool_use = {
        "type": "assistant",
        "message": {
            "content": [
                {"type": "thinking", "thinking": ""},
                {
                    "type": "tool_use",
                    "id": "toolu_01",
                    "name": "mcp__weather__get_forecast",
                    "input": {"date": "2026-11-28"},
                },
            ]
        },
    }
    tool_result = {
        "type": "user",
        "message": {
            "content": [
                {"type": "tool_result", "tool_use_id": "toolu_01", "content": '{"rain_mm": 6.8}'}
            ]
        },
    }
    [request] = describe(tool_use)
    [answer] = describe(tool_result)
    assert "id=toolu_01" in request and 'get_forecast({"date": "2026-11-28"})' in request
    assert "tool_use_id=toolu_01" in answer and "rain_mm" in answer


def test_error_results_are_flagged_and_list_content_is_joined():
    event = {
        "type": "user",
        "message": {
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "toolu_02",
                    "is_error": True,
                    "content": [{"type": "text", "text": "Use get_past_weather"}],
                }
            ]
        },
    }
    [line] = describe(event)
    assert "ERROR  Use get_past_weather" in line


def test_raw_mode_adds_the_json_block():
    event = {
        "type": "assistant",
        "message": {"content": [{"type": "tool_use", "id": "t", "name": "x", "input": {}}]},
    }
    assert describe(event, raw=True)[-1].startswith("  raw: {")


def test_unknown_events_print_nothing():
    assert describe({"type": "rate_limit_event"}) == []


def test_command_disables_builtin_tools_and_allows_only_ours():
    command = build_command("claude", "question")
    assert command[command.index("--tools") + 1] == ""
    assert "mcp__weather__get_forecast" in command[command.index("--allowedTools") + 1]


def test_next_saturday():
    assert next_saturday(date(2026, 11, 25)) == date(2026, 11, 28)
    assert next_saturday(date(2026, 11, 28)) == date(2026, 11, 28)
