from __future__ import annotations

import subprocess

from celery import Celery
from .celery_scheduler import celeryapp
from settings.logging_settings import LOGGING_SETTINGS
from settings.celery_settings import CELERY_SETTINGS
from loguru import logger as log
import setup

def run():
    log.debug(f"Celery app ({type(celeryapp.app)}): {celeryapp.app}")

    celeryapp.app.autodiscover_tasks(
        packages=[
            "scheduling.celery_scheduler.celery_tasks.weatherapi_tasks"
        ]
    )

    try:
        worker = celeryapp.app.worker_main(
            argv=["worker", "--loglevel=DEBUG", "--uid=0", "--gid=0"]
        )
    except Exception as exc:
        msg = Exception(f"Unhandled exception getting Celery worker. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc
    
    if worker is None:
        raise ValueError(f"Celery app.worker_main() returned None. This could be an issue authenticating to the broker/backend. Check the Celery logs for details.")

    log.info("Starting Celery worker")
    try:
        worker.start()
    except Exception as exc:
        msg = Exception(f"Unhandled exception starting Celery worker. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

# def run():
#     subprocess.run(["celery", "-A", "scheduling.celery_scheduler.celeryapp", "worker", "--loglevel=DEBUG"])

# def run_beat():
#     subprocess.run(["celery", "-A", "scheduling.celery_scheduler.celeryapp", "beat", "--loglevel=DEBUG"])

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    setup.setup_database()

    run()
