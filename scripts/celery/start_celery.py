from __future__ import annotations

import argparse

from celery import Celery
from loguru import logger as log
from scheduling.celery_scheduler import (
    CelerySettings,
    celery_settings,
    celeryapp,
    check_task,
    start_celery,
    start_celery_beat,
    start_celery_worker,
)
from settings import APP_SETTINGS, LOGGING_SETTINGS, DB_SETTINGS, CELERY_SETTINGS
import setup

def parse_args():
    parser = argparse.ArgumentParser(
        description="Start the Celery application in worker or beat mode."
    )
    parser.add_argument(
        "-m", "--mode",
        type=str,
        choices=["worker", "beat"],
        required=True,
        help="Mode to run the application: 'worker' or 'beat'."
    )
    return parser.parse_args()


def run(app: Celery, mode: str):
    log.debug(f"Celery mode: {mode}")
    
    try:
        start_celery.start(app=celeryapp.app, mode=mode)
    except Exception as e:
        log.error(f"Failed to start application: {e}")
        return False

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), log_fmt="basic", colorize=True)
    try:
        setup.setup_database()
    except Exception as exc:
        msg = f"({type(exc)}) Error setting up database. Details: {exc}"
        log.error(msg)
        
        raise
    
    log.debug(f"""
[App settings]
{APP_SETTINGS.as_dict()}

[Logging settings]
{LOGGING_SETTINGS.as_dict()}

Database settings]
{DB_SETTINGS.as_dict()}

[Celery settings]
{CELERY_SETTINGS.as_dict()}
""")
    
    args = parse_args()
    
    if not args.mode:
        log.error(f"[WARNING] Missing a --mode (-m). Please re-run with -m ['beat', 'worker'] (choose 1).")
        exit(1)
        
    try:
        run(app=celeryapp.app, mode=args.mode.lower())
    except Exception as exc:
        msg = f"({type(exc)}) Error running Celery in '{args.mode}' mode. Details: {exc}"
        log.error(msg)
        
        raise exc
    