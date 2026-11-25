from datetime import date

from party_demo.local_calendar import list_events, resolve_day

WEDNESDAY = date(2026, 11, 25)


def test_resolve_day_is_relative_to_the_current_week():
    assert resolve_day("this", "Saturday", WEDNESDAY) == date(2026, 11, 28)
    assert resolve_day("last", "Saturday", WEDNESDAY) == date(2026, 11, 21)


def test_list_events_filters_by_date_range():
    events = list_events(date(2026, 11, 23), date(2026, 11, 29), WEDNESDAY)
    assert [event.title for event in events] == [
        "Office game night",
        "Year-end garden party",
        "Kids birthday picnic",
    ]


def test_event_description_carries_the_setting():
    events = list_events(date(2026, 11, 21), date(2026, 11, 21), WEDNESDAY)
    assert events[0].to_dict()["description"] == "Setting: outdoor"
