from __future__ import annotations

from functools import lru_cache
import typing as t

## Import celery tasks
# from .celery_tasks import ...

import celery
from celery import Celery
from celery.result import AsyncResult
from celery.schedules import crontab
from scheduling.celery_scheduler.celeryconfig import CelerySettings, celery_settings, return_rabbitmq_url, return_redis_url
from settings.celery_settings import CELERY_SETTINGS

from loguru import logger as log


app: Celery = Celery(
    "celery_tasks",
    # broker=celery_settings.broker_url,
    broker=return_rabbitmq_url(),
    # backend=celery_settings.backend_url,
    backend=return_redis_url(),
    include=[
        ## Include paths to celery task modules, i.e.
        #  "scheduling.celery_scheduler.celery_tasks.scheduled"
    ]
)

## Set app config
app.conf.update(timezonee="America/New_York", enable_utc=True)

## Periodic jobs
@app.on_after_finalize.connect
def scheduled_tasks(sender, **kwargs):
    ## Call task_current_comic() every hour. Use imported schedule
    # app.conf.beat_schedule = <scheduled task name
    pass


log.debug(f"Discovered Celery tasks: {app.tasks}")

def check_task(task_id: str = None, app: Celery = app) -> AsyncResult | None:
    """Check a Celery task by its ID.

    Params:
        task_id (str): The Celery task's ID.
        app (Celery): An initialized Celery app.

    Returns:
        (AsyncResult): Returns a Celery `AsyncResult` object, if task is found.
        (None): If no task is found or an exception occurs.

    """
    assert task_id, ValueError("Missing a Celery task_id")
    task_id: str = f"{task_id}"

    log.info(f"Checking Celery task '{task_id}'")
    try:
        task_res: AsyncResult = app.AsyncResult(task_id)

        return task_res
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting task by ID '{task_id}'. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        return None
