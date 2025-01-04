from __future__ import annotations

from pathlib import Path
import time
import typing as t

from celery import current_app
from celery.result import AsyncResult
import db
import depends
from domain.weatherapi.location import LocationIn, LocationModel, LocationOut, LocationRepository
from domain.weatherapi.weather import current as domain_current_weather, forecast as domain_forecast_weather, weather_alerts as domain_weather_alerts
from weather_client.apis import api_weatherapi

import httpx

from loguru import logger as log


@current_app.task(name="request_current_weather")
def task_current_weather(location: str) -> dict:
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
