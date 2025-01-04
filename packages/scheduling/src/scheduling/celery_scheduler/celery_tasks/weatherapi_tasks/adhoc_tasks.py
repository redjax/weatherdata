from __future__ import annotations

from celery import current_app, shared_task
import db
from depends import db_depends
from domain.weatherapi import (
    location as domain_location,
    weather as domain_weather,
)
from domain.weatherapi.location import (
    LocationIn,
    LocationModel,
    LocationOut,
    LocationRepository,
)
from domain.weatherapi.weather.current import (
    CurrentWeatherIn,
    CurrentWeatherModel,
    CurrentWeatherOut,
    CurrentWeatherRepository,
)
from domain.weatherapi.weather.forecast import (
    ForecastJSONIn,
    ForecastJSONModel,
    ForecastJSONOut,
    ForecastJSONRepository,
)
from loguru import logger as log
from weather_client.apis import api_weatherapi

@log.catch
@current_app.task(name="weatherapi-current-weather")
def task_adhoc_current_weather(location: str = api_weatherapi.settings.location_name, api_key: str = api_weatherapi.settings.api_key, use_cache: bool = False):
    """Get the current weather for a location using a Celery task.
    
    Params:
        location (str): The location to get the current weather for.
        api_key (str): The API key to use for the request.
        use_cache (bool): Whether to use the cache for the request.
    """
    try:
        current_weather_res = api_weatherapi.client.get_current_weather(location=location, api_key=api_key, use_cache=use_cache)
    except Exception as exc:
        msg = f"({type(exc)}) Error requesting current weather as a Celery ad-hoc task. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    return current_weather_res


@log.catch
@current_app.task(name="weatherapi-weather-forecast")
def task_adhoc_weather_forecast(location: str = api_weatherapi.settings.location_name, api_key: str = api_weatherapi.settings.api_key, use_cache: bool = False):
    """Get the forecast weather for a location using a Celery task.
    
    Params:
        location (str): The location to get the forecast weather for.
        api_key (str): The API key to use for the request.
        use_cache (bool): Whether to use the cache for the request.
    """
    try:
        forecast_weather_res = api_weatherapi.client.get_weather_forecast(location=location, api_key=api_key, use_cache=use_cache)
    except Exception as exc:
        msg = f"({type(exc)}) Error requesting forecast weather as a Celery ad-hoc task. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    return forecast_weather_res