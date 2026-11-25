# Party Planner: Tools, MCP, Connectors, Skills, Plugins

One small problem, solved one layer higher at each step:

> "Which of my celebrations last week and this week were, or will be, hit by rain in Kigali?"

| Step | Concept | What it proves |
|---|---|---|
| 1 | **Tool** | A tool is a name + description + schema + function. Claude only *requests* a call; the result comes back matched by id. |
| 2 | **MCP** | The same tools plug into any MCP app without glue code. |
| 3 | **Connector** | Hosted MCP + *your* Google sign-in. Claude acts as you, in every Claude app. |
| 4 | **Skill** | Same tools, better behaviour: our rules for rain and backups. |
| 5 | **Plugin** | Everything above, installed in one command. |

No API key needed. Everything runs on your normal Claude Code login.

## Layout

```
party-planner/
├─ src/party_demo/
│  ├─ inspect_tools.py          Step 1a: list tools + call one directly (no AI)
│  ├─ watch_tool_calls.py       Step 1b: watch tool_use / tool_result live
│  ├─ calendar_server.py        pretend calendar as an MCP server (Steps 1-2)
│  └─ local_calendar.py         reads demo/events.json
├─ demo/
│  ├─ events.json               sample celebrations, dates relative to the current week
│  └─ step1.mcp.json            which MCP servers Step 1 uses
├─ plugins/                     a local plugin marketplace
│  └─ party-planner/            Step 5: the plugin
│     ├─ weather-server/          Step 2: weather MCP server (Open-Meteo, no API key)
│     ├─ skills/rain-plan/        Step 4: the skill
│     ├─ commands/party-check.md  /party-check
│     ├─ hooks/                   trace hook: every tool call → tool_trace.log
│     └─ .mcp.json                tells Claude Code how to start the server
└─ tests/
```

The weather rules live in one place (`weather-server/src/party_weather/service.py`) and every step reuses them.

## Setup (once)

```powershell
uv sync                 # installs Python 3.12 + dependencies
uv run pytest -q        # unit tests, no network
```

- The `claude` command: `party-watch` finds the copy bundled with the VS Code extension by itself. For the `claude mcp ...` commands below, install the Claude Code CLI or add that folder to PATH.
- **Step 3** needs the Google Calendar connector in claude.ai, signed in with the **second** Google account (the one with the demo calendar).

## The demo

### Step 1. Tool: what Claude sees, what it sends

**1a. A tool is just a function with a schema.**

```powershell
uv run party-tools
```

Prints every tool exactly as an AI app receives it (name, description, `input_schema`), then calls `get_forecast` directly. **No AI involved.** There's nothing magic about a tool.

**1b. Watch Claude invoke the tools.**

```powershell
uv run party-watch            # add --raw to show the raw JSON blocks
```

Runs Claude Code headless with **only** our tools (built-in tools switched off). Point at:
- `→ tool_use id=toolu_…  get_forecast({"date": …})`: this is all Claude produces, a request.
- `← tool_result tool_use_id=toolu_…`: the answer, matched to its request by id.
- Several `tool_use` lines in a row before any results: Claude asked for several calls at once.
- Claude chose `get_past_weather` for past dates and `get_forecast` for upcoming ones, using only the tool descriptions.
- Without the skill (Step 4), it also checks the weather for **indoor** events. Remember this for later.

### Step 2. MCP: the same tools, any app

```powershell
claude mcp add weather -- uv run --project plugins/party-planner/weather-server party-weather-mcp
claude mcp add calendar -- uv run party-calendar-mcp
```

In Claude Code: `/mcp` lists both servers and their tools. Ask *"Will it rain in Kigali on Saturday?"*
The trace shows `MCP server  mcp__weather__get_forecast`. The servers didn't change between Step 1 and Step 2; only the app using them did. That's what MCP gives you.

### Step 3. Connector: hosted, signed in, everywhere

1. `claude mcp remove calendar`. Ask *"What celebrations do I have this week?"* Claude can't see your calendar.
2. claude.ai → Settings → Connectors → **Google Calendar** → Connect → pick the second account → approve.
3. Ask again. The trace now shows `connector  mcp__claude_ai_...`. Open claude.ai in the browser or on your phone: the same connector works there without any setup.

Seed the demo calendar once (in Claude Code, after signing in):

> Create the events in `demo/events.json` in my Google Calendar. Resolve `week` + `weekday` relative to the current week. Put `Setting: <setting>` in each description.

**Turn your MCP server into a connector:**

```powershell
uv run --project plugins/party-planner/weather-server party-weather-mcp --http --port 8000
cloudflared tunnel --url http://localhost:8000      # or: ngrok http 8000
```

claude.ai → Settings → Connectors → **Add custom connector** → `https://<tunnel-host>/mcp`.
Ask claude.ai on the web about Kigali weather. **Same code, now a connector.** (In an org account, an owner may need to allow custom connectors.)

| | Local MCP server | Connector |
|---|---|---|
| Runs | your laptop | hosted |
| Set up by | `claude mcp add` | a click in settings |
| Sign-in | none | OAuth, acts as you |
| Works in | that one app | web, desktop, mobile, Claude Code |

### Step 4. Skill: same tools, our rules

Ask *"Which of my celebrations are affected by rain?"* without the skill, then with it.
With the skill, Claude skips weather calls for indoor events, applies the 60% / 5 mm thresholds, uses our table and asks before changing the calendar. The trace shows `skill  Skill {"skill": "...rain-plan"}`, followed by fewer and better-chosen calls.

### Step 5. Plugin: one install

```powershell
claude mcp remove weather                         # the plugin brings its own copy
```

In Claude Code:

```
/plugin marketplace add ./plugins
/plugin install party-planner@party-demo
/party-check
```

One install brought the MCP server, the skill, `/party-check` and the trace hook. A teammate runs the same two lines.

## If the weather doesn't cooperate

Set `$env:PARTY_SIMULATE_RAIN = "1"` before running `party-watch` or `claude`. Forecasts then return 85% / 14 mm, marked `"simulated": true`, so the "at risk" branch always runs. Past weather is never simulated.
