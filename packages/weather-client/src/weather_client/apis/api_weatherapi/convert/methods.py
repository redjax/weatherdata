from __future__ import annotations

import typing as t
import json

from domain.weatherapi.location import LocationIn
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
from loguru import logger as log

__all__ = [
    "current_weather_dict_to_schema",
    "location_dict_to_schema",
    "current_weather_schema_to_model",
    "weather_forecast_dict_to_schema",
    "current_weather_api_response_to_dict",
    "current_weather_api_response_dict_to_schemas"
]

@log.catch
def current_weather_dict_to_schema(current_weather_dict: dict):
    """Convert a current weather dictionary to a CurrentWeatherIn schema.
    
    Params:
        current_weather_dict (dict): The current weather dictionary to convert.
        
    Returns:
        CurrentWeatherIn: The converted CurrentWeatherIn schema.

    """
    current_weather: CurrentWeatherIn = CurrentWeatherIn.model_validate(
        current_weather_dict
    )

    return current_weather


@log.catch
def location_dict_to_schema(location_dict: dict):
    """Convert a location dictionary to a LocationIn schema.
    
    Params:
        location_dict (dict): The location dictionary to convert.
        
    Returns:
        LocationIn: The converted LocationIn schema.

    """
    location: LocationIn = LocationIn.model_validate(location_dict)

    return location


@log.catch
def current_weather_schema_to_model(current_weather_schema: CurrentWeatherIn):
    """Convert a current weather schema to a database model.
    
    Params:
        current_weather_schema (CurrentWeatherIn): The current weather schema to convert.
        
    Returns:
        CurrentWeatherModel: The converted database model.

    """
    raise NotImplementedError(
        "Converting current weather schema to database model not yet supported."
    )
    # current_weather_model: CurrentWeatherModel = CurrentWeatherModel(
    #     **current_weather_schema.model_dump()
    # )

    # return current_weather_model


@log.catch
def weather_forecast_dict_to_schema(weather_forecast_dict: dict) -> ForecastJSONIn:
    """Convert a weather forecast dictionary to a ForecastJSONIn schema.
    
    Params:
        weather_forecast_dict (dict): The weather forecast dictionary to convert.
        
    Returns:
        ForecastJSONIn: The converted ForecastJSONIn schema.

    """
    weather_forecast_json: ForecastJSONIn = ForecastJSONIn(
        forecast_json=weather_forecast_dict
    )

    return weather_forecast_json

@log.catch
def current_weather_api_response_to_dict(content: t.Union[dict, str, bytes]):
    if content is None:
        raise ValueError("Missing response content to convert")
    if isinstance(content, str):
        log.debug("Decoding response content string")
        content: dict = json.load(content)
    if isinstance(content, bytes):
        log.debug(f"Decoding content bytestring")
        content_str: str = content.decode("utf-8")
        content: dict = json.load(content_str)
    if isinstance(content, dict):
        return content
    
    return content


@log.catch
def current_weather_api_response_dict_to_schemas(content_dict: dict) -> list[dict[str, t.Union[LocationIn, CurrentWeatherIn]]]:
    if not content_dict:
        raise ValueError("Missing a content dict to decode into objects")
    if not isinstance(content_dict, dict):
        raise TypeError(f"Invalid type for content_dict: {type(content_dict)}. Must be a dict.")
    
    current_weather_dict: dict = content_dict["current"]
    location_dict: dict = content_dict["location"]
    
    return_obj: dict[str, t.Union[LocationIn, CurrentWeatherIn]] = {"location": None, "current_weather": None}
    
    try:
        current_weather: CurrentWeatherIn = current_weather_dict_to_schema(current_weather_dict)
        return_obj["current_weather"] = current_weather
    except Exception as exc:
        msg = f"({type(exc)}) Error converting current weather dict to CurrentWeatherIn schema. Details: {exc}"
        log.error(msg)
        
    try:
        location: LocationIn = location_dict_to_schema(location_dict)
        return_obj["location"] = location
    except Exception as exc:
        msg = f"({type(exc)}) Error converting location dict to LocationIn schema.  Details: {exc}"
    
    return return_obj
    