from __future__ import annotations

from .celery_scheduler import celeryapp

from celery import Celery
from loguru import logger as log
from settings.celery_settings import CELERY_SETTINGS
from settings.logging_settings import LOGGING_SETTINGS
import setup

def run():
    log.debug(f"Celery app ({type(celeryapp.app)}): {celeryapp.app}")

    log.debug(f"Celery Beat schedule: {celeryapp.app.Beat().schedule}")
    try:
        log.info(f"Starting Celery Beat")
        celeryapp.app.Beat(loglevel=CELERY_SETTINGS.get("CELERY_LOG_LEVEL", default="INFO").lower()).run()
    except Exception as exc:
        msg = Exception(f"Unhandled exception starting Celery Beat. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    setup.setup_database()

    run()
