from loguru import logger as log

import setup
from settings import OPENMETEO_SETTINGS
from depends import db_depends
from weather_client.apis import api_openmeteo

def main():
    log.debug(f"OpenMeteo settings: {OPENMETEO_SETTINGS.as_dict()}")
    
    log.debug(f"Location name: {api_openmeteo.location_name} (lat: {api_openmeteo.location_lat}, lon: {api_openmeteo.location_lon})")

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level="DEBUG", colorize=True)
    
    main()

