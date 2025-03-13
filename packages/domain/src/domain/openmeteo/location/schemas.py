from decimal import Decimal
import typing as t

from loguru import logger as log
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    computed_field,
    field_validator,
)

__all__ = [
    "LocationIn",
    "LocationOut",
]

class LocationBase(BaseModel):
    """OpenMetro Location schema (base model).
    
    Params:
        id (int): The ID of the location.
        name (str): The name of the location.
        latitude (Decimal): The latitude of the location.
        longitude (Decimal): The longitude of the location.
        elevation (Decimal): The elevation of the location.
        feature_code (str): The feature code of the location.
        country_code (str): The country code of the location.
        admin1_id (int): The admin1 ID of the location.
        admin2_id (int): The admin2 ID of the location.
        admin3_id (int): The admin3 ID of the location.
        timezone (str): The timezone of the location.
        population (int): The population of the location.
        postcodes (list[str]): The postcodes of the location.
        country_id (int): The country ID of the location.
        country (str): The country of the location.
        admin1 (str): The admin1 of the location.
        admin2 (str): The admin2 of the location.
        admin3 (str): The admin3 of the location.
    """
    id: int
    name: str
    latitude: Decimal
    longitude: Decimal
    elevation: Decimal
    feature_code: str
    country_code: str
    admin1_id: int
    admin2_id: int
    admin3_id: int
    timezone: str
    population: int
    postcodes: list[str]
    country_id: int
    country: str
    admin1: str
    admin2: str
    admin3: str
    
class LocationIn(LocationBase):
    """OpenMetro Location schema.
    
    Params:
        id (int): The ID of the location.
        name (str): The name of the location.
        latitude (Decimal): The latitude of the location.
        longitude (Decimal): The longitude of the location.
        elevation (Decimal): The elevation of the location.
        feature_code (str): The feature code of the location.
        country_code (str): The country code of the location.
        admin1_id (int): The admin1 ID of the location.
        admin2_id (int): The admin2 ID of the location.
        admin3_id (int): The admin3 ID of the location.
        timezone (str): The timezone of the location.
        population (int): The population of the location.
        postcodes (list[str]): The postcodes of the location.
        country_id (int): The country ID of the location.
        country (str): The country of the location.
        admin1 (str): The admin1 of the location.
        admin2 (str): The admin2 of the location.
        admin3 (str): The admin3 of the location.
    """

class LocationOut(LocationBase):
    """OpenMetro Location schema from the database.
    
    Params:
        location_id (int): The ID of the location in the database.
        
        id (int): The ID of the location.
        name (str): The name of the location.
        latitude (Decimal): The latitude of the location.
        longitude (Decimal): The longitude of the location.
        elevation (Decimal): The elevation of the location.
        feature_code (str): The feature code of the location.
        country_code (str): The country code of the location.
        admin1_id (int): The admin1 ID of the location.
        admin2_id (int): The admin2 ID of the location.
        admin3_id (int): The admin3 ID of the location.
        timezone (str): The timezone of the location.
        population (int): The population of the location.
        postcodes (list[str]): The postcodes of the location.
        country_id (int): The country ID of the location.
        country (str): The country of the location.
        admin1 (str): The admin1 of the location.
        admin2 (str): The admin2 of the location.
        admin3 (str): The admin3 of the location.
    """
    location_id: int