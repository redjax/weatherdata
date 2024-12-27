from __future__ import annotations

import settings
from core_utils import time_utils
from domain.exc import FileProcessingError
from http_lib import (
    HttpxController,
    build_request,
    client,
    get_http_controller,
    merge_headers,
)
import httpx
from loguru import logger as log
import setup
from domain.weatherapi import location, weather

from weather_client.apis import api_weatherapi

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"))

    log.debug("Test debug log")
    log.debug(f"WeatherAPI API key: {settings.WEATHERAPI_SETTINGS.get('WEATHERAPI_API_KEY', default=None)}")
    
    ts = time_utils.get_ts(as_str=True, safe_str=True)
    log.debug(f"Example timestamp: {ts}")
    
    req = build_request(url="https://www.google.com")
    
    log.info("Making test request to google.com")
    with get_http_controller() as http_ctl:
        res: httpx.Response = http_ctl.client.send(req)
        print(f"[{res.status_code}: {res.reason_phrase}]")
        
    try:
        current_weather = api_weatherapi.client.get_current_weather(use_cache=True)
    except Exception as exc:
        msg = f"({type(exc)}) Error getting current weather. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    log.info(f"Location: {current_weather['location']}")
    location_schema = location.LocationIn.model_validate(current_weather["location"])
    log.debug(f"Location schema: {location_schema}")
    
    log.info(f"Current weather: {current_weather}")
    current_weather_schema = weather.current.CurrentWeatherIn.model_validate(current_weather["current"])
    log.debug(f"Current weather schema: {current_weather_schema}")
    
    try:
        weather_forecast = api_weatherapi.client.get_weather_forecast()
    except Exception as exc:
        msg = f"({type(exc)}) Error getting weather forecast. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    log.info(f"Weather forecast: {weather_forecast}")
    weather_forecast_schema = weather.forecast.ForecastJSONIn(forecast_json=weather_forecast["forecast"])
    log.debug(f"Weather forecast schema: {weather_forecast_schema}")