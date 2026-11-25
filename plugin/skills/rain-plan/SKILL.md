---
name: rain-plan
description: Rain-check celebrations and parties in Kigali using the Outlook calendar and the weather tools. Use when asked whether rain affected, or will affect, parties, celebrations or events.
---

# Rain plan

## 1. Find the celebrations

- Use the **Outlook calendar** (Microsoft 365 connector). Do not use any other calendar.
- Search with the query `Setting`: every celebration has a line `Setting: indoor` or `Setting: outdoor`. Never list the whole calendar, which also holds private and work meetings.
- Default window: Monday of last week to Sunday of this week.
- Event times come back in UTC. Show them in Kigali time (UTC+2).

## 2. Check the weather only where it matters

- **Indoor events: no weather check.** Do not call a weather tool for them.
- Outdoor event already over: `get_past_weather`.
- Outdoor event today or later: `get_forecast`.
- Always pass the event's `start_time` and `end_time` in Kigali time, so the tool returns the rain **during the event**, not just the day.

## 3. Judge each outdoor event

Judge on the event's hours (`event_rain_mm`, `event_rain_probability_pct`), not the daily totals.

- Past: **rained out** if `event_rain_mm` is 2 or more, otherwise **dry**.
- Upcoming: **at risk** if `event_rain_probability_pct` is 60 or more, or `event_rain_mm` is 2 or more, otherwise **looks fine**.
- When the day was wet but the event's hours were not, say so: it is the most useful thing to know.
- If a weather tool fails, say which events could not be checked. Do not guess.

## 4. Answer in this format

| Event | When (Kigali) | Setting | Weather | Verdict |
|---|---|---|---|---|

Then, only for events that are **at risk**:
- Suggest an indoor backup (a covered area at the venue, or the office).
- Draft a short message to guests: at most 60 words, friendly, states the plan.

The calendar is read-only for you: suggest changes, never claim to have made them.
