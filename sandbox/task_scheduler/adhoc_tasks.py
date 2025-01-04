from __future__ import annotations

import time

from celery.result import AsyncResult
import db
import depends
from loguru import logger as log
from scheduling.celery_scheduler import celeryapp, check_task
from settings.celery_settings import CELERY_SETTINGS
from settings.logging_settings import LOGGING_SETTINGS
import setup

demo_db_dict = {"drivername": "sqlite+pysqlite", "username": None, "password": None, "host": None, "port": None, "database": ".db/demo.sqlite3"}

def demo_db_engine(db_conf: dict = demo_db_dict, echo: bool = False):
    db_uri = db.get_db_uri(**db_conf)
    engine = db.get_engine(url=db_uri, echo=echo)
    
    return engine


def adhoc_current_weather():
    try:
        async_res: AsyncResult = celeryapp.app.send_task("weatherapi-current-weather")
    except Exception as exc:
        msg = f"({type(exc)}) Error running Celery worker. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    result = async_res.get(timeout=30)
    log.info(f"Task completed! Result: {result}")
    

def adhoc_weather_forecast():
    try:
        async_res: AsyncResult = celeryapp.app.send_task("weatherapi-weather-forecast")
    except Exception as exc:
        msg = f"({type(exc)}) Error running Celery worker. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    result = async_res.get(timeout=30)
    log.info(f"Task completed! Result: {result}")

def main():
    log.info("Sending task to Celery")
    
    adhoc_current_weather()
    adhoc_weather_forecast()

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    
    ## Create a demo.sqlite3 database separate from app's database
    demo_db_uri = depends.get_db_uri(**demo_db_dict)
    setup.setup_database(engine=depends.get_db_engine(db_uri=demo_db_uri))
    
    log.debug(f"Celery settings: {CELERY_SETTINGS.as_dict()}")
    
    main()    
    
