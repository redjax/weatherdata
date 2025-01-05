from __future__ import annotations

import db
import depends
from loguru import logger as log
from scheduling import start_celery_worker
from settings.celery_settings import CELERY_SETTINGS
from settings.logging_settings import LOGGING_SETTINGS
import setup

def run():
    log.debug(f"Celery settings: {CELERY_SETTINGS.as_dict()}")
    
    log.info("Starting Celery worker.")
    try:
        start_celery_worker.run()
    except Exception as exc:
        msg = f"({type(exc)}) Error running Celery worker. Details: {exc}"
        log.error(msg)
        
        raise exc


if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    log.add("logs/celery_worker.log", retention=3, rotation="15 MB", level="DEBUG")
    log.add("logs/celery_worker_error.log", retention=3, rotation="15 MB", level="ERROR")
    
    setup.setup_database()
    
    run()
