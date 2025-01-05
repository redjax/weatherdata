from __future__ import annotations

from celery.result import AsyncResult
import db
import depends
from loguru import logger as log
from settings.logging_settings import LOGGING_SETTINGS
import setup
import sqlalchemy as sa
from weather_client.apis import api_weatherapi

demo_db_dict = {"drivername": "sqlite+pysqlite", "username": None, "password": None, "host": None, "port": None, "database": ".db/demo.sqlite3"}

def demo_db_engine(db_conf: dict = demo_db_dict, echo: bool = False):
    db_uri = db.get_db_uri(**db_conf)
    engine = db.get_engine(url=db_uri, echo=echo)
    
    return engine


def count_db_current_weather(db_engine: sa.Engine, echo: bool = False):
    try:
        return api_weatherapi.db_client.current_weather.count_current_weather(engine=db_engine, echo=echo)
    except Exception as exc:
        msg = f"({type(exc)}) Error counting number of current weather rows. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    
def count_db_weather_forecast(db_engine: sa.Engine, echo: bool = False):
    try:
        return api_weatherapi.db_client.forecast.count_weather_forecast(engine=db_engine, echo=echo)
    except Exception as exc:
        msg = f"({type(exc)}) Error counting number of weather forecast rows. Details: {exc}"
        log.error(msg)
        
        raise exc
    

def count_db_locations(db_engine: sa.Engine, echo: bool = False):
    try:
        return api_weatherapi.db_client.location.count_locations(db_engine, echo=echo)
    except Exception as exc:
        msg = f"({type(exc)}) Error counting number of locations. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    
def main(db_engine: sa.Engine = depends.get_db_engine(), db_echo: bool = False):
    current_weather_count = count_db_current_weather(db_engine=db_engine, echo=db_echo)
    forecast_count = count_db_weather_forecast(db_engine=db_engine, echo=db_echo)
    location_count = count_db_locations(db_engine=db_engine, echo=db_echo)
    
    log.info(f"Number of current weather rows: {current_weather_count}")
    log.info(f"Number of weather forecast rows: {forecast_count}")
    log.info(f"Number of locations: {location_count}")
    

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    
    ## Create a demo.sqlite3 database separate from app's database
    # demo_db_uri = depends.get_db_uri(**demo_db_dict)
    # setup.setup_database(engine=depends.get_db_engine(db_uri=demo_db_uri))
    
    setup.setup_database()
    
    main()
