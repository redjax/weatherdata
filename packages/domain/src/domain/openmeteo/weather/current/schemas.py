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


class MeteoMinutely15UnitsIn(BaseModel):
    time: str
    temperature_2m: str
    precipitation: str
    weather_code: str
    wind_direction_80m: str
    is_day: str | None = Field(default=None)
    relative_humidity_2m: str
    rain: str
    wind_gusts_10m: str
    wind_speed_10m: str
    dew_point_2m: str
    snowfall: str
    wind_speed_80m: str
    visibility: str
    apparent_temperature: str
    sunshine_duration: str
    wind_direction_10m: str


class MeteoMinutely15UnitsOut(BaseModel):
    id: int


class MeteoMinutely15In(BaseModel):
    time: list[str] = Field(default_factory=list)
    temperature_2m: list[str] = Field(default_factory=list)
    precipitation: list[Decimal] = Field(default_factory=list)
    weather_code: list[int] = Field(default_factory=list)
    wind_direction_80m: list[int] = Field(default_factory=list)
    is_dat: list[int] = Field(default_factory=list)
    relative_humidity_2m: list[int] = Field(default_factory=list)
    rain: list[Decimal] = Field(default_factory=list)
    wind_gusts_10m: list[Decimal] = Field(default_factory=list)
    wind_speed_10m: list[Decimal] = Field(default_factory=list)
    dew_point_2m: list[Decimal] = Field(default_factory=list)
    snowfall: list[Decimal] = Field(default_factory=list)
    wind_speed_80m: list[Decimal] = Field(default_factory=list)
    visibility: list[Decimal] = Field(default_factory=list)
    apparent_temperature: list[Decimal] = Field(default_factory=list)
    sunshine_duration: list[Decimal] = Field(default_factory=list)
    wind_direction_10m: list[int] = Field(default_factory=list)


class MeteoMinutely15UnitsOut(MeteoMinutely15In):
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
    current: MeteoCurrentIn
    minutely_15_units: MeteoMinutely15UnitsIn


class MeteoCurrentWeatherOut(MeteoCurrentWeatherIn):
    id: int

    current_units: MeteoCurrentWeatherUnitsOut
    current: MeteoCurrentOut
