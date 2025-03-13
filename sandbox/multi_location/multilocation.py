import typing as t
from decimal import Decimal
from pathlib import Path
import json

import setup
from core_utils import path_utils
from weather_client.apis import api_weatherapi
from domain.weatherapi import location as location_domain
from domain.weatherapi.weather import current as current_weather_domain
from domain.weatherapi.weather import forecast as forecast_weather_domain
from domain.weatherdata_api import responses as weatherdata_api_responses_domain

from loguru import logger as log
from pydantic import BaseModel, Field, field_validator, ValidationError

import weather_client.apis


class LocationBase(BaseModel):
    name: str
    lat: str
    lon: str
    
    @property
    def lat_as_float(self) -> float:
        return float(self.lat)
    
    @property
    def lon_as_float(self) -> float:
        return float(self.lon)
    
    @property
    def lat_as_decimal(self) -> Decimal:
        return Decimal(self.lat)
    
    @property
    def lon_as_decimal(self) -> Decimal:
        return Decimal(self.lon)
    
class LocationIn(LocationBase):
    pass

class LocationOut(LocationBase):
    id: int


LOCATIONS_FILE: str = "./sandbox/multi_location/locations.json"


def load_locations(locations_file: str) -> list[dict]:
    if not Path(locations_file).exists():
        raise FileNotFoundError(f"Could not find locations file at '{locations_file}'")

    log.info(f"Reading locations from file '{locations_file}'")
    with open(locations_file, "r") as f:
        locations: dict = json.load(f)

    return locations


def main(locations_file: str):
    location_dicts: list[dict] = load_locations(locations_file)
    log.info(f"Loaded [{len(location_dicts)}] location(s) from file")
    
    log.debug(f"Location dicts: {location_dicts}")
    
    locations: list[LocationIn] = [LocationIn.model_validate(loc) for loc in location_dicts]
    log.debug(f"Locations: {locations}")
    log.debug(f"{locations[0].name} lon as Decimal: ({type(locations[0].lon_as_decimal)}) {locations[0].lon_as_decimal}")
    
    current_weather_response_dicts: list[dict] = []
    
    for location in locations:
        log.debug(f"REQUEST current weather in {location.name}")
        try:
            current_weather: dict | None = api_weatherapi.client.get_current_weather(location=location.name)
            if current_weather:
                current_weather_response_dicts.append(current_weather)
        except Exception as exc:
            msg = f"({type(exc)}) Error requesting weather in {location.name}. Details: {exc}"
            log.error(msg)
            
            continue
        
        log.info(f"Weather in '{location.name}': {current_weather}")
        
    log.info(f"Requested weather successfully for [{len(current_weather_response_dicts)}/{len(locations)}] location(s)")
    
    current_weather_response_schemas: list[dict[str, t.Union[current_weather_domain.CurrentWeatherIn, location_domain.LocationIn]]] = []
    for d in current_weather_response_dicts:
        try:
            _current_weather_schema = api_weatherapi.convert.current_weather_dict_to_schema(d["current"])
            _location_schema = api_weatherapi.convert.location_dict_to_schema(d["location"])
            current_weather_response_schemas.append({"current_weather": _current_weather_schema, "location": _location_schema})
        except Exception as exc:
            msg = f"({type(exc)}) error converting dict to schema. Details: {exc}"
            log.error(msg)
            
            continue
    log.debug(f"Current weather response schema classes: {current_weather_response_schemas}")

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level="DEBUG", colorize=True)
    
    main(locations_file=LOCATIONS_FILE)