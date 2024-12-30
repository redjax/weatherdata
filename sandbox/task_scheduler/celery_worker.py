from settings.celery_settings import CELERY_SETTINGS
from settings.logging_settings import LOGGING_SETTINGS
from loguru import logger as log

import setup

from scheduling import start_celery_worker

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    setup.setup_database()
    
    log.debug(f"Celery settings: {CELERY_SETTINGS.as_dict()}")
    
    log.info("Starting Celery worker.")
    try:
        start_celery_worker.run()
    except Exception as exc:
        msg = f"({type(exc)}) Error running Celery worker. Details: {exc}"
        log.error(msg)
        
        raise exc
