from __future__ import annotations

from decimal import Decimal
import typing as t

from db import Base, annotated

from loguru import logger as log
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so

__all__ = [
    "MeteoCurrentWeatherUnitsModel",
    "MeteoCurrentModel",
    "MeteoMinutely15UnitsModel",
]


class MeteoCurrentWeatherUnitsModel(Base):
    __tablename__ = "meteo_current_weather_units"

    id: so.Mapped[annotated.INT_PK]

    time: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    interval: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    temperature_2m: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    relative_humidity_2m: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    apparent_temperature: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    is_day: so.Mapped[t.Optional[str]] = so.mapped_column(sa.TEXT, nullable=True)
    precipitation: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    rain: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    showers: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    snowfall: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    weather_code: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    cloud_cover: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    pressure_msl: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    surface_pressure: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    wind_speed_10m: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    wind_direction_10m: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    wind_gusts_10m: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)


class MeteoCurrentModel(Base):
    __tablename__ = "meteo_current_weather"

    id: so.Mapped[annotated.INT_PK]

    time: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    interval: so.Mapped[int] = so.mapped_column(sa.NUMERIC, nullable=False)
    temperature_2m: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=10, scale=2), nullable=False
    )
    relative_humidity_2m: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=10, scale=2), nullable=False
    )
    apparent_temperature: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=10, scale=2), nullable=False
    )
    is_day: so.Mapped[int] = so.mapped_column(sa.Numeric, nullable=False)
    precipitation: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=10, scale=2), nullable=False
    )
    rain: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=10, scale=2), nullable=False
    )
    showers: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=10, scale=2), nullable=False
    )
    snowfall: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=10, scale=2), nullable=False
    )
    weather_code: so.Mapped[int] = so.mapped_column(sa.Numeric, nullable=False)
    cloud_cover: so.Mapped[int] = so.mapped_column(sa.Numeric, nullable=False)
    pressure_msl: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=10, scale=2), nullable=False
    )
    surface_pressure: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=10, scale=2), nullable=False
    )
    wind_speed_10m: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=10, scale=2), nullable=False
    )
    wind_direction_10m: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=10, scale=2), nullable=False
    )
    wind_gusts_10m: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=10, scale=2), nullable=False
    )


class MeteoMinutely15UnitsModel(Base):
    __tablename__ = "meteo_minutely_15_units"

    id: so.Mapped[annotated.INT_PK]

    time: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    temperature_2m: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    precipitation: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    weather_code: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
