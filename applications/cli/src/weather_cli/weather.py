from __future__ import annotations

from datetime import timedelta
import typing as t

from core_utils import time_utils
from cyclopts import App, Group, Parameter
from domain.weatherapi import (
    location as location_domain,
    weather as weather_domain,
)
from loguru import logger as log
from weather_client.apis import api_weatherapi

from depends import db_depends

__all__ = ["weather_app"]

weather_app = App(name="weather", help="CLI for getting weather data")


@weather_app.command(name="current")
def get_current_weather(
    location: t.Annotated[str, Parameter(
        name="location",
        show_default=True,
        help="The location to get the current weather for. Can be a city name or postal code."
    )] = "London",
    save_to_db: t.Annotated[bool, Parameter(name="--save-db", show_default=True)] = False
) -> weather_domain.current.CurrentWeatherIn:
    """Get the current weather for a given location.
    
    Params:
        location: The location to get the current weather for. Can be a city name or postal code.
    
    Returns:
        The current weather for the given location.

    """
    log.info(f"Getting current weather for location: {location}")
    
    try:
        current_weather_res = api_weatherapi.client.get_current_weather(location=location)
    except Exception as exc:
        msg = f"({type(exc)}) Error getting current weather for location '{location}'. Details: {exc}"
        log.error(msg)
        
        exit(1)
        
    location: location_domain.LocationIn = location_domain.LocationIn.model_validate(current_weather_res["location"])
    log.debug(f"Location schema: {location}")
    
    current_weather: weather_domain.current.CurrentWeatherIn = weather_domain.current.CurrentWeatherIn.model_validate(current_weather_res["current"])
    log.debug(f"Current weather schema: {current_weather}")

    current_weather_str: str = f"""
[ Current Weather for: '{location.name}, {location.region} ({location.country})' ]

Temperature: {current_weather.heatindex_f} °F
Feels Like: {current_weather.feelslike_f} °F
Humidity: {current_weather.humidity} %
Pressure: {current_weather.pressure_in} inHg
Visibility: {current_weather.vis_km} km
Last Updated: {current_weather.last_updated}
Weather Condition: {current_weather.condition.text}
Wind:
    Speed (KPH): {current_weather.wind_kph} kph
    Speed (MPH): {current_weather.wind_mph} mph
    Windchill: {current_weather.windchill_f} °F
    Direction: {current_weather.wind_dir}
    Degree: {current_weather.wind_degree} degrees
"""

    if save_to_db:
        log.info("Saving raw current weather response to database")
        try:
            saved_current_weather_response: weather_domain.current.CurrentWeatherJSONOut = api_weatherapi.db_client.save_current_weather_response(current_weather_schema=current_weather_res, engine=db_depends.get_db_engine())
        except Exception as exc:
            msg = f"({type(exc)}) Error saving raw current weather response to database. Details: {exc}"
            log.error(msg)
        
        
        log.info("Saving current weather to database")
        
        try:
            saved_current_weather: weather_domain.current.CurrentWeatherOut = api_weatherapi.db_client.save_current_weather(location=location, current_weather=current_weather, engine=db_depends.get_db_engine())
            log.info(f"Saved current weather to database: {saved_current_weather}")
        except Exception as exc:
            msg = f"({type(exc)}) Error saving current weather to database. Details: {exc}"
            log.error(msg)

    log.info(current_weather_str)
    
    return current_weather
    

@weather_app.command(name="forecast")
def get_weather_forecast(location: t.Annotated[str, Parameter(name="location", show_default=True)] = "London", save_to_db: t.Annotated[bool, Parameter(name="--save-db", show_default=True)] = False) -> weather_domain.forecast.ForecastJSONIn:
    """Get the weather forecast for a given location.
    
    Params:
        location: The location to get the weather forecast for. Can be a city name or postal code.
    """
    log.info(f"Getting weather forecast for location: {location}")
    
    try:
        forecast_res = api_weatherapi.client.get_weather_forecast(location=location)
    except Exception as exc:
        msg = f"({type(exc)}) Error getting weather forecast for location '{location}'. Details: {exc}"
        log.error(msg)
        
        exit(1)
        
    log.debug(f"Weather forecast response: {forecast_res}")
        
    location: location_domain.LocationIn = location_domain.LocationIn.model_validate(forecast_res["location"])
    log.debug(f"Location schema: {location}")
    
#     current_weather: weather_domain.current.CurrentWeatherIn = weather_domain.current.CurrentWeatherIn.model_validate(current_weather_res["current"])
    forecast_json: weather_domain.forecast.ForecastJSONIn = weather_domain.forecast.ForecastJSONIn(forecast_json=forecast_res["forecast"])
    log.debug(f"Weather forecast schema: {forecast_json}")
    
    weather_forecast_str: str = f"""
[ Weather forecast for: '{location.name}, {location.region} ({location.country})' ]

[NotImplemented]
"""

    log.info(weather_forecast_str)
    
    if save_to_db:
        log.info(f"Saving weather forecast to database")
        
        try:
            saved_forecast: weather_domain.forecast.ForecastJSONOut = api_weatherapi.db_client.save_forecast(forecast_schema=forecast_json, engine=db_depends.get_db_engine())
            log.info(f"Saved weather forecast to database: {saved_forecast}")
        except Exception as exc:
            msg = f"({type(exc)}) Error saving weather forecast to database. Details: {exc}"
            log.error(msg)
    
    return weather_forecast_str
