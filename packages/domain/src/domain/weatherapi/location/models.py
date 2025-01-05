from __future__ import annotations

from decimal import Decimal
import typing as t

from db import Base, annotated
from loguru import logger as log
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so

class LocationModel(Base):
    """Location Model.
    
    Attributes:
        id (int): The ID of the location record.
        name (str): The name of the location.
        region (str): The region of the location.
        country (str): The country of the location.
        lat (Decimal): The latitude of the location.
        lon (Decimal): The longitude of the location.
        tz_id (str): The time zone ID of the location.
        localtime_epoch (int): The local time epoch of the location.
        localtime (str): The local time of the location.
        current_weather_entries (list[CurrentWeatherModel]): The current weather entries for the location.
        forecast_weather_entries (list[ForecastDayModel]): The forecast weather entries for the location.
    
    Relationships:
        current_weather_entries (list[CurrentWeatherModel]): The current weather entries for the location.
        forecast_weather_entries (list[ForecastDayModel]): The forecast weather entries for the location.

    """
    
    __tablename__ = "weatherapi_location"
    __table_args__ = (sa.UniqueConstraint("name", "country", name="_name_country_uc"),)

    id: so.Mapped[annotated.INT_PK]

    name: so.Mapped[str] = so.mapped_column(sa.TEXT)
    region: so.Mapped[str] = so.mapped_column(sa.TEXT)
    country: so.Mapped[str] = so.mapped_column(sa.TEXT)
    lat: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    lon: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    tz_id: so.Mapped[str] = so.mapped_column(sa.TEXT)
    localtime_epoch: so.Mapped[int] = so.mapped_column(sa.NUMERIC)
    localtime: so.Mapped[str] = so.mapped_column(sa.TEXT)

    # Relationship to CurrentWeatherModel using a string reference
    current_weather_entries: so.Mapped[list["CurrentWeatherModel"]] = so.relationship(
        "CurrentWeatherModel", back_populates="location", cascade="all, delete-orphan"
    )

    # Relationship to ForecastDayModel
    # forecast_weather_entries: so.Mapped[list["ForecastDayModel"]] = so.relationship(
    #     "ForecastDayModel", back_populates="location", cascade="all, delete-orphan"
    # )