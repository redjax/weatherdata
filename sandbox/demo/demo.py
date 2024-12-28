from __future__ import annotations

from core_utils import time_utils
import db
import depends
import depends.db_depends
from domain.exc import FileProcessingError
from domain.weatherapi import location, weather
from http_lib import (
    HttpxController,
    build_request,
    client,
    get_http_controller,
    merge_headers,
)
import httpx
from loguru import logger as log
import settings
import setup
from weather_client.apis import api_weatherapi

def demo_ts():
    ts = time_utils.get_ts(as_str=True, safe_str=True)
    log.debug(f"Example timestamp: {ts}")


def demo_request(use_http_cache: bool = True):
    req = build_request(url="https://www.google.com")
    
    log.info("Making test request to google.com")
    with get_http_controller() as http_ctl:
        res: httpx.Response = http_ctl.client.send(req)
        print(f"[{res.status_code}: {res.reason_phrase}]")
        
    try:
        current_weather = api_weatherapi.client.get_current_weather(use_cache=use_http_cache)
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
        weather_forecast = api_weatherapi.client.get_weather_forecast(use_cache=use_http_cache)
    except Exception as exc:
        msg = f"({type(exc)}) Error getting weather forecast. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    log.info(f"Weather forecast: {weather_forecast}")
    weather_forecast_schema = weather.forecast.ForecastJSONIn(forecast_json=weather_forecast["forecast"])
    log.debug(f"Weather forecast schema: {weather_forecast_schema}")

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"))
    
    ## Create a demo.sqlite3 database separate from app's database
    demo_db_uri = depends.get_db_uri(drivername="sqlite+pysqlite", database=".db/demo.sqlite3")
    setup.setup_database(engine=depends.get_db_engine(db_uri=demo_db_uri))

    log.debug("Test debug log")
    log.debug(f"WeatherAPI API key: {settings.WEATHERAPI_SETTINGS.get('WEATHERAPI_API_KEY', default=None)}")
    log.debug(f"Database settings: {settings.DB_SETTINGS.as_dict()}")
    
    demo_ts()
    demo_request()
