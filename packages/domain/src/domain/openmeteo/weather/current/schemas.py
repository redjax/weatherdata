from __future__ import annotations

from decimal import Decimal
import typing as t

from loguru import logger as log
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    computed_field,
    field_validator,
)

__all__ = [
    "MeteoCurrentWeatherIn",
    "MeteoCurrentWeatherOut",
    "MeteoCurrentWeatherUnitsIn",
    "MeteoCurrentWeatherUnitsOut",
    "MeteoCurrentIn",
    "MeteoCurrentOut",
]


class MeteoCurrentWeatherUnitsIn(BaseModel):
    time: str
    interval: str
    temperature_2m: str
    relative_humidity_2m: str
    apparent_temperature: str
    is_day: str | None = Field(default=None)
    precipitation: str
    rain: str
    showers: str
    snowfall: str
    weather_code: str
    cloud_cover: str
    pressure_msl: str
    surface_pressure: str
    wind_speed_10m: str
    wind_direction_10m: str
    wind_gusts_10m: str


class MeteoCurrentWeatherUnitsOut(MeteoCurrentWeatherUnitsIn):
    id: int


class MeteoCurrentIn(BaseModel):
    time: str
    interval: int
    temperature_2m: Decimal
    relative_humidity_2m: Decimal
    apparent_temperature: Decimal
    is_day: int
    precipitation: Decimal
    rain: Decimal
    showers: Decimal
    snowfall: Decimal
    weather_code: int
    cloud_cover: int
    pressure_msl: Decimal
    surface_pressure: Decimal
    wind_speed_10m: Decimal
    wind_direction_10m: Decimal
    wind_gusts_10m: Decimal


class MeteoCurrentOut(MeteoCurrentIn):
    id: int


## Main class


class MeteoCurrentWeatherIn(BaseModel):
    latitude: Decimal
    longitude: Decimal
    generationtime_ms: Decimal
    utc_offset_seconds: Decimal
    timezone: str
    timezone_abbreviation: str
    elevation: Decimal
    current_units: MeteoCurrentWeatherUnitsIn


class MeteoCurrentWeatherOut(MeteoCurrentWeatherIn):
    id: int

    current_units: MeteoCurrentWeatherUnitsOut
