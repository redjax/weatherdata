from __future__ import annotations

from . import (
    CelerySettings,
    celery_settings,
    celeryapp,
    check_task,
    start_celery_beat,
    start_celery_worker,
)

from celery import Celery
from loguru import logger as log
from settings.logging_settings import LOGGING_SETTINGS
import setup

def worker(app: Celery):
    log.info("Starting Celery worker.")
    try:
        start_celery_worker(app=app)
    except Exception as exc:
        msg = f"({type(exc)}) Error running Celery worker. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    log.info("Celery worker stopped.")
    
def beat(app: Celery):
    log.info("Starting Celery beat.")
    try:
        start_celery_beat(app=app)
    except Exception as exc:
        msg = f"({type(exc)}) Error running Celery beat. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    log.info("Celery beat stopped.")

def start(app: Celery, mode: str):
    if mode not in ["worker", "beat"]:
        log.error(f"Unknown mode: {mode}")
        
        raise ValueError(f"Invalid mode: {mode}. Must be one of ['worker', 'beat']")

    match mode.lower():
        case "worker":
            worker(app=app)
        case "beat":
            beat(app=app)
        case _:
            log.error(f"Unknown mode: {mode}")
            
            raise ValueError(f"Invalid mode: {mode}.")
