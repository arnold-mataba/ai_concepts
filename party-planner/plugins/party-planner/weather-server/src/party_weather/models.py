from dataclasses import asdict, dataclass, replace
from datetime import date

SIMULATED_RAIN_MM = 14.0
SIMULATED_RAIN_PROBABILITY_PCT = 85


@dataclass(frozen=True)
class DailyWeather:
    day: date
    summary: str
    rain_mm: float
    rain_probability_pct: int | None
    max_temp_c: float | None
    simulated: bool = False

    def with_simulated_rain(self) -> "DailyWeather":
        return replace(
            self,
            summary="Heavy rain (simulated)",
            rain_mm=max(self.rain_mm, SIMULATED_RAIN_MM),
            rain_probability_pct=SIMULATED_RAIN_PROBABILITY_PCT,
            simulated=True,
        )

    def without_probability(self) -> "DailyWeather":
        return replace(self, rain_probability_pct=None)

    def to_dict(self) -> dict[str, object]:
        return {**asdict(self), "day": self.day.isoformat()}
