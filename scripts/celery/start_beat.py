from __future__ import annotations

import db
import depends
from loguru import logger as log
from scheduling.celery_scheduler import celeryapp, start_celery
from settings.celery_settings import CELERY_SETTINGS
from settings.logging_settings import LOGGING_SETTINGS
import setup

from celery import Celery

def run(app: Celery):
    log.debug(f"Celery settings: {CELERY_SETTINGS.as_dict()}")
    
    log.info("Starting Celery Beat.")
    try:
        start_celery.beat(app=app)
    except Exception as exc:
        msg = f"({type(exc)}) Error running Celery worker. Details: {exc}"
        log.error(msg)
        
        raise exc

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    log.add("logs/celery_beat.log", retention=3, rotation="15 MB", level="DEBUG")
    log.add("logs/celery_beat_error.log", retention=3, rotation="15 MB", level="ERROR")
    
    setup.setup_database()
    
    run(app=celeryapp.app)
