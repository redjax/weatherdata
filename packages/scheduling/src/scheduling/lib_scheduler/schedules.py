from weather_client.apis import api_weatherapi
import schedule
from loguru import logger as log

__all__ = ["sched_every_15m_weatherapi_current_weather"]


def sched_every_15m_weatherapi_current_weather(location: str, save_to_db: bool):
    log.info(
        f"Starting schedule, requesting current weather for location '{location}' every 15th minute"
    )

    job_details = {
        "func": api_weatherapi.client.get_current_weather,
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
