from __future__ import annotations

import db
import depends
from loguru import logger as log
from scheduling.celery_scheduler import start_celery, celeryapp
from settings.celery_settings import CELERY_SETTINGS
from settings.logging_settings import LOGGING_SETTINGS
import setup

demo_db_dict = {"drivername": "sqlite+pysqlite", "username": None, "password": None, "host": None, "port": None, "database": ".db/demo.sqlite3"}

def demo_db_engine(db_conf: dict = demo_db_dict, echo: bool = False):
    db_uri = db.get_db_uri(**db_conf)
    engine = db.get_engine(url=db_uri, echo=echo)
    
    return engine

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    log.add("sandbox/task_scheduler/logs/celery_worker.log", retention=3, rotation="15 MB", level="DEBUG")
    log.add("sandbox/task_scheduler/logs/celery_worker_error.log", retention=3, rotation="15 MB", level="ERROR")
    
    ## Create a demo.sqlite3 database separate from app's database
    demo_db_uri = depends.get_db_uri(**demo_db_dict)
    setup.setup_database(engine=depends.get_db_engine(db_uri=demo_db_uri))
    
    log.debug(f"Celery settings: {CELERY_SETTINGS.as_dict()}")
    
    log.info("Starting Celery worker.")
    try:
        start_celery.worker(app=celeryapp.app)
    except Exception as exc:
        msg = f"({type(exc)}) Error running Celery worker. Details: {exc}"
        log.error(msg)
        
        raise exc
