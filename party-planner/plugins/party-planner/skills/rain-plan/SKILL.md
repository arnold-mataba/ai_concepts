---
name: rain-plan
description: Rain-check celebrations and parties in Kigali using the calendar and the weather tools. Use when asked about parties, celebrations or events together with weather or rain, or whether an event should move indoors.
---

# Rain plan

How we decide whether rain affects a celebration, and what to do about it.

## Steps

1. **Get the events.** List calendar events for the window asked about. Default window: Monday of last week to Sunday of this week.
2. **Decide the setting.** Each event description has a line `Setting: outdoor` or `Setting: indoor`. If the line is missing, infer it from the location (park, garden, eco-park, terrace = outdoor) and say that you inferred it.
3. **Check weather only for outdoor events.** Never call a weather tool for an indoor event.
   - Event already happened: call `get_past_weather`.
   - Event today or later: call `get_forecast`.
   - Check each date once, even if several events share it.
4. **Judge each outdoor event.**
   - Past event: **rained out** if `rain_mm` is 5 or more, otherwise **dry**.
   - Upcoming event: **at risk** if `rain_probability_pct` is 60 or more, or `rain_mm` is 5 or more, otherwise **looks fine**.
   - If the weather result has `"simulated": true`, say so next to the verdict.

## Output

A table, then actions:

| Event | When | Setting | Weather | Verdict |
|---|---|---|---|---|

**Proposed actions**, only for events that are at risk:
- Suggest an indoor backup (a covered space at the same venue, or the office).
- Draft a guest message: at most 80 words, friendly, states the plan, no alarm.

For past events that were rained out, add one line on what to do differently next time.

## Changing the calendar

- Always ask before changing the calendar.
- When the user agrees, create a **new** event named `[Backup] <original title>` at the same time, with the reason in its description.
- Never move, edit or delete the original event.
