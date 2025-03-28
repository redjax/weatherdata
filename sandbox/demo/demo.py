from __future__ import annotations

import os

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

demo_db_dict = {"drivername": "sqlite+pysqlite", "username": None, "password": None, "host": None, "port": None, "database": ".db/demo.sqlite3"}

def demo_ts():
    ts = time_utils.get_ts(as_str=True, safe_str=True)
    log.debug(f"Example timestamp: {ts}")
    
    
def demo_db_engine(db_conf: dict = demo_db_dict, echo: bool = False):
    db_uri = db.get_db_uri(**db_conf)
    engine = db.get_engine(url=db_uri, echo=echo)
    
    return engine


def demo_request(use_http_cache: bool = True):
    req = build_request(url="https://www.google.com")
    
    log.info("Making test request to google.com")
    with get_http_controller() as http_ctl:
        res: httpx.Response = http_ctl.client.send(req)
        print(f"[{res.status_code}: {res.reason_phrase}]")
        

def demo_current_weather(use_http_cache: bool = True):
    try:
        current_weather = api_weatherapi.client.get_current_weather(use_cache=use_http_cache)
    except Exception as exc:
        msg = f"({type(exc)}) Error getting current weather. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    log.info(f"Location: {current_weather['location']}")
    location_schema = location.LocationIn.model_validate(current_weather["location"])
    log.debug(f"Location schema: {location_schema}")
    
    ## Save location to db
    try:
        db_location = api_weatherapi.db_client.location.save_location(location=location_schema, engine=demo_db_engine())
        log.success("Saved location to database")
        log.debug(f"Location from database: {db_location}")
    except Exception as exc:
        msg = f"({type(exc)}) Error saving location to database: {exc}"
        log.error(msg)

    log.info(f"Current weather: {current_weather}")
    current_weather_schema = weather.current.CurrentWeatherIn.model_validate(current_weather["current"])
    log.debug(f"Current weather schema: {current_weather_schema}")
    
    ## Save current weather to db
    try:
        db_current_weather = api_weatherapi.db_client.current_weather.save_current_weather(location=location_schema, current_weather=current_weather_schema, engine=demo_db_engine())
        log.success("Saved current weather to database")
        log.debug(f"Current weather from database: {db_current_weather}")
    except Exception as exc:
        msg = f"({type(exc)}) Error saving current weather to database: {exc}"
        log.error(msg)


def demo_weather_forecast(use_http_cache: bool = True):
    try:
        weather_forecast = api_weatherapi.client.get_weather_forecast(use_cache=use_http_cache)
    except Exception as exc:
        msg = f"({type(exc)}) Error getting weather forecast. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    log.info(f"Weather forecast: <output too large>")
    weather_forecast_schema = weather.forecast.ForecastJSONIn(forecast_json=weather_forecast["forecast"])
    log.debug(f"Weather forecast schema: <output too large>")
    
    ## Save weather forecast JSON to database
    try:
        db_weather_forecast = api_weatherapi.db_client.forecast.save_forecast(forecast_schema=weather_forecast_schema, engine=demo_db_engine())
        log.success("Saved weather forecast to database")
        # log.debug(f"Weather forecast from database: {db_weather_forecast}")
    except Exception as exc:
        msg = f"({type(exc)}) Error saving weather forecast to database: {exc}"
        log.error(msg)

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"))
    
    ## Create a demo.sqlite3 database separate from app's database
    demo_db_uri = depends.get_db_uri(**demo_db_dict)
    setup.setup_database(engine=depends.get_db_engine(db_uri=demo_db_uri))

    log.debug("Test debug log")
    log.debug(f"WeatherAPI API key: {settings.WEATHERAPI_SETTINGS.get('WEATHERAPI_API_KEY', default=None)}")
    log.debug(f"Database settings: {settings.DB_SETTINGS.as_dict()}")
    
    demo_ts()
    demo_request()
    
    demo_current_weather()
    demo_weather_forecast()
