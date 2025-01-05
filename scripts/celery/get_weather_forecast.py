from __future__ import annotations

from celery.result import AsyncResult
import db
import depends
from loguru import logger as log
from scheduling.celery_scheduler import celeryapp, check_task
from settings.celery_settings import CELERY_SETTINGS
from settings.logging_settings import LOGGING_SETTINGS
import setup

def main():
    try:
        async_res: AsyncResult = celeryapp.app.send_task("weatherapi-weather-forecast")
    except Exception as exc:
        msg = f"({type(exc)}) Error running Celery worker. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    result = async_res.get(timeout=30)
    log.info(f"Task completed! Result: {result}")
    

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    
    setup.setup_database()
    
    log.debug(f"Celery settings: {CELERY_SETTINGS.as_dict()}")
    
    main() 