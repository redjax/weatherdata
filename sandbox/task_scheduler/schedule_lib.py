import db
import depends
from loguru import logger as log
from settings.logging_settings import LOGGING_SETTINGS
from settings.weatherapi_settings import WEATHERAPI_SETTINGS
import setup
import schedule
import time
import weather_client
import weather_client.apis
import weather_client.apis.api_weatherapi


def _request_weather(location: str, save_to_db: bool):
    log.info(f"Requesting weather in '{location}'.")

    current_weather: dict = (
        weather_client.apis.api_weatherapi.client.get_current_weather(
            location=location, save_to_db=save_to_db
        )
    )

    return current_weather


def sched_15m_current_weather(location: str, save_to_db: bool = True):
    job_details = {
        "func": _request_weather,
        "kwargs": {"location": location, "save_to_db": save_to_db},
    }

    schedule.every().hour.at(":15").do(job_details["func"], **job_details["kwargs"])

    try:
        while True:
            schedule.run_pending()
    except KeyboardInterrupt:
        log.error("Interrupted by user")
        return
    except Exception as exc:
        log.error(f"Error requesting weather in location '{location}'. Details: {exc}")
        raise

    # return current_weather


if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LOG_LEVEL", "INFO"))
    log.debug("Debug logging enabled")

    sched_15m_current_weather(
        location=WEATHERAPI_SETTINGS.get("WEATHERAPI_LOCATION_NAME", "London"),
        save_to_db=True,
    )
