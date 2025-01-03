from __future__ import annotations

from typing import NoReturn

from domain.weatherapi.weather.current import (
    CurrentWeatherIn,
    CurrentWeatherModel,
    CurrentWeatherOut,
)
from domain.weatherapi.weather.forecast import (
    ForecastJSONIn,
    ForecastJSONModel,
    ForecastJSONOut,
    ForecastJSONRepository,
)
from domain.weatherapi.location import LocationIn

from loguru import logger as log

@log.catch
def current_weather_dict_to_schema(current_weather_dict: dict):
    current_weather: CurrentWeatherIn = CurrentWeatherIn.model_validate(
        current_weather_dict
    )

    return current_weather


@log.catch
def location_dict_to_schema(location_dict: dict):
    location: LocationIn = LocationIn.model_validate(location_dict)

    return location


@log.catch
def current_weather_schema_to_model(current_weather_schema: CurrentWeatherIn):
    raise NotImplementedError(
        "Converting current weather schema to database model not yet supported."
    )
    # current_weather_model: CurrentWeatherModel = CurrentWeatherModel(
    #     **current_weather_schema.model_dump()
    # )

    # return current_weather_model


@log.catch
def weather_forecast_dict_to_schema(weather_forecast_dict: dict) -> ForecastJSONIn:
    weather_forecast_json: ForecastJSONIn = ForecastJSONIn(
        forecast_json=weather_forecast_dict
    )

    return weather_forecast_json