import argparse

from loguru import logger as log

import setup
from settings.logging_settings import LOGGING_SETTINGS
from scheduling.celery_scheduler import start_celery, start_celery_worker, start_celery_beat, CelerySettings, check_task, celery_settings, celeryapp

from celery import Celery


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
    setup.setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    setup.setup_database()
    
    args = parse_args()
    
    if not args.mode:
        print(f"[WARNING] Missing a --mode (-m). Please re-run with -m ['beat', 'worker'] (choose 1).")
        exit(1)
        
    try:
        run(app=celeryapp.app, mode=args.mode.lower())
    except Exception as exc:
        msg = f"({type(exc)}) Error running Celery in '{args.mode}' mode. Details: {exc}"
        log.error(msg)
        
        raise exc
    