from loguru import logger as log

import typing as t
import json

import setup
from settings import OPENMETEO_SETTINGS
from depends import db_depends
import http_lib
from weather_client.apis import api_openmeteo
from domain.openmeteo import location as openmeteo_location_domain

import httpx
import hishel


def main():
    log.debug(f"OpenMeteo settings: {OPENMETEO_SETTINGS.as_dict()}")

    log.debug(
        f"Location name: {api_openmeteo.location_name} (lat: {api_openmeteo.location_lat}, lon: {api_openmeteo.location_lon})"
    )

    log.info(f"Searching for location '{api_openmeteo.location_name}")
    location: openmeteo_location_domain.LocationIn = (
        api_openmeteo.client.search_location(
            location_name=api_openmeteo.location_name, results_limit=1, language="en"
        )
    )
    log.debug(f"Location ({type(location)}): {location}")

    log.info(f"Saving location '{api_openmeteo.location_name}' to database")
    location_model: openmeteo_location_domain.MeteoLocationModel = (
        api_openmeteo.convert.location_schema_to_model(location)
    )
    if location_model:
        log.debug(f"Location model: {location_model.__dict__}")
    else:
        log.warning(f"location_model is None and should not be.")

    log.info(f"Requesting current weather for location '{location.name}'")
    current_weather = api_openmeteo.client.request_current_weather(
        location_name=location.name, lat=location.latitude, lon=location.longitude
    )

    log.info(
        f"It is {current_weather['current']['temperature_2m']} F in {location.name}"
    )

    # with open("ex_openmeteo_current.json", "w") as f:
    #     _data = json.dumps(current_weather, indent=4, default=str)
    #     f.write(_data)


if __name__ == "__main__":
    setup.setup_loguru_logging(log_level="DEBUG", colorize=True)

    main()
