import logging

from scheduling import lib_scheduler
import setup
from settings import WEATHERAPI_SETTINGS, LOGGING_SETTINGS

log = logging.getLogger(__name__)

if __name__ == "__main__":
    setup.setup_loguru_logging(
        log_level=LOGGING_SETTINGS.get("LOG_LEVEL", "INFO").upper(), colorize=True
    )

    lib_scheduler.sched_every_15m_weatherapi_current_weather(
        location=WEATHERAPI_SETTINGS.get("WEATHERAPI_LOCATION_NAME", "London"),
        save_to_db=True,
    )
