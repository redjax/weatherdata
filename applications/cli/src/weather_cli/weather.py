from __future__ import annotations

import typing as t
from datetime import timedelta

from core_utils import time_utils
from domain.weatherapi import weather as weather_domain
from domain.weatherapi import location as location_domain
from weather_client.apis import api_weatherapi

from cyclopts import App, Group, Parameter

from loguru import logger as log


weather_app = App(name="weather", help="CLI for getting weather data")


@weather_app.command(name="current")
def get_current_weather(location: t.Annotated[str, Parameter(name="location", show_default=True)] = "London"):
    """Get the current weather for a given location.
    
    Params:
        location: The location to get the current weather for. Can be a city name or postal code.
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

    log.info(current_weather_str)
    

@weather_app.command(name="forecast")
def get_weather_forecast(location: t.Annotated[str, Parameter(name="location", show_default=True)] = "London"):
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
