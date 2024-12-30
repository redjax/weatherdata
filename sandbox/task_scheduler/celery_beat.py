from settings.celery_settings import CELERY_SETTINGS
from settings.logging_settings import LOGGING_SETTINGS
from loguru import logger as log

import setup

from scheduling import start_celery_beat

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    setup.setup_database()
    
    start_celery_beat.run()
