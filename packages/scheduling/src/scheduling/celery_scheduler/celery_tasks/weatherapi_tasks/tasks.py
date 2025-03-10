from __future__ import annotations

from pathlib import Path
import time
import typing as t

from celery import current_app
from celery.result import AsyncResult
import db
import depends
from domain.weatherapi.location import (
    LocationIn,
    LocationModel,
    LocationOut,
    LocationRepository,
)
from domain.weatherapi.weather import (
    current as domain_current_weather,
    forecast as domain_forecast_weather,
    weather_alerts as domain_weather_alerts,
)
import httpx
from loguru import logger as log
from weather_client.apis import api_weatherapi

__all__ = [
    "task_current_weather",
    "task_weather_forecast",
]

@current_app.task(name="request_current_weather")
def task_current_weather(location: str) -> dict:
    """Request the current weather for a location using a Celery task.
    
    Params:
        location (str): The location to get the current weather for.
        
    Returns:
        (dict): The current weather for the location.
        (None): None if the request failed.

    """
    log.info("Requesting current weather from WeatherAPI")
    
    try:
        current_weather_dict = api_weatherapi.client.get_current_weather(location=location, save_to_db=True, use_cache=True)
        if current_weather_dict is None:
            log.error("Failed to retrieve current weather from weatherapi.")
            return None
        
        log.success(f"Retrieved current weather for location '{location}'.")
    except Exception as exc:
        msg = f"({type(exc)}) Error requesting current weather from weatherapi. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    return current_weather_dict


@current_app.task(name="request_weather_forecast")
def task_weather_forecast(location: str) -> dict:
    """Request the weather forecast for a location using a Celery task.
    
    Params:
        location (str): The location to get the weather forecast for.
        
    Returns:
        (dict): The weather forecast for the location.
        (None): None if the request failed.

    """
    log.info("Requesting weather forecast from WeatherAPI")
    
    try:
        weather_forecast_dict = api_weatherapi.client.get_weather_forecast(location=location, save_to_db=True, use_cache=True)
        if weather_forecast_dict is None:
            log.error("Failed to retrieve weather forecast from weatherapi.")
            return None
        
        log.success(f"Retrieved weather forecast for location '{location}'.")
    except Exception as exc:
        msg = f"({type(exc)}) Error requesting weather forecast from weatherapi. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    return weather_forecast_dict
