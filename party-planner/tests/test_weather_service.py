from datetime import date, timedelta

import pytest
from party_weather.models import DailyWeather
from party_weather.open_meteo import describe_weather_code, parse_daily
from party_weather.service import DateOutOfRangeError, WeatherService, parse_iso_date

TODAY = date(2026, 11, 25)


class FakeProvider:
    def __init__(self) -> None:
        self.calls: list[date] = []

    def daily(self, day: date) -> DailyWeather:
        self.calls.append(day)
        return DailyWeather(day, "Partly cloudy", 0.4, 20, 26.0)


def make_service(simulate_rain: bool = False) -> tuple[WeatherService, FakeProvider]:
    provider = FakeProvider()
    return WeatherService(provider, simulate_rain=simulate_rain, today=lambda: TODAY), provider


def test_forecast_returns_provider_weather():
    service, provider = make_service()
    weather = service.forecast(TODAY + timedelta(days=3))
    assert weather.rain_probability_pct == 20
    assert provider.calls == [TODAY + timedelta(days=3)]


def test_forecast_rejects_past_dates_without_calling_the_api():
    service, provider = make_service()
    with pytest.raises(DateOutOfRangeError, match="get_past_weather"):
        service.forecast(TODAY - timedelta(days=1))
    assert provider.calls == []


def test_past_weather_rejects_today_and_drops_probability():
    service, _ = make_service()
    with pytest.raises(DateOutOfRangeError, match="get_forecast"):
        service.past_weather(TODAY)
    assert service.past_weather(TODAY - timedelta(days=4)).rain_probability_pct is None


def test_simulated_rain_applies_to_forecasts_only():
    service, _ = make_service(simulate_rain=True)
    forecast = service.forecast(TODAY)
    assert forecast.simulated and forecast.rain_probability_pct == 85
    assert not service.past_weather(TODAY - timedelta(days=1)).simulated


def test_parse_daily_reads_first_day():
    payload = {
        "daily": {
            "time": ["2026-11-28"],
            "weather_code": [63],
            "temperature_2m_max": [24.5],
            "precipitation_sum": [11.2],
            "precipitation_probability_max": [78],
        }
    }
    weather = parse_daily(payload)
    assert weather == DailyWeather(date(2026, 11, 28), "Rain", 11.2, 78, 24.5)


@pytest.mark.parametrize(
    ("code", "label"), [(0, "Clear sky"), (81, "Rain showers"), (None, "Unknown")]
)
def test_describe_weather_code(code, label):
    assert describe_weather_code(code) == label


def test_parse_iso_date_gives_a_helpful_error():
    with pytest.raises(ValueError, match="2026-11-28"):
        parse_iso_date("next saturday")
