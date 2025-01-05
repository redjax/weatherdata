from loguru import logger as log

import setup
from settings.logging_settings import LOGGING_SETTINGS
from . import start_celery_worker, start_celery_beat, CelerySettings, check_task, celery_settings, celeryapp

from celery import Celery


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
