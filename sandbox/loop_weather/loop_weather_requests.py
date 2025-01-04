from __future__ import annotations

import time

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

def return_engine(db_conf: dict = demo_db_dict, echo: bool = False):
    db_uri = db.get_db_uri(**db_conf)
    engine = db.get_engine(url=db_uri, echo=echo)
    
    return engine

def _current_weather(use_http_cache: bool = True):
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
        db_location = api_weatherapi.db_client.location.save_location(location=location_schema, engine=return_engine())
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
        db_current_weather = api_weatherapi.db_client.current_weather.save_current_weather(location=location_schema, current_weather=current_weather_schema, engine=return_engine())
        log.success("Saved current weather to database")
        log.debug(f"Current weather from database: {db_current_weather}")
    except Exception as exc:
        msg = f"({type(exc)}) Error saving current weather to database: {exc}"
        log.error(msg)


def _weather_forecast(use_http_cache: bool = True):
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
        db_weather_forecast = api_weatherapi.db_client.forecast.save_forecast(forecast_schema=weather_forecast_schema, engine=return_engine())
        log.success("Saved weather forecast to database")
        # log.debug(f"Weather forecast from database: {db_weather_forecast}")
    except Exception as exc:
        msg = f"({type(exc)}) Error saving weather forecast to database: {exc}"
        log.error(msg)
        

def main(limit: int | None = 96, loop_sleep: int = 900):
    loops: int = 0
    
    while True:
        if limit:
            log.info(f"Looping {limit} time(s)")

            if loops > limit:
                log.info(f"Looped [{loops}/{limit}] time(s)")
                
                break
            
        current_weather = _current_weather()
        weather_forecast = _weather_forecast()
        
        loops += 1
        
        log.info(f"Sleeping for {loop_sleep} second(s)")
        if limit:
            log.info(f"Loop [{loops}/{limit}]")
        else:
            log.info(f"Loop count: {loops}")
        
        time.sleep(loop_sleep)
        
    log.info(f"Looped [{loops}] time(s)")


if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"))
    setup.setup_database(engine=return_engine())
    
    main(limit=0)
