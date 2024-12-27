from __future__ import annotations

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

class LocationIn(BaseModel):
    name: str
    region: str
    country: str
    lat: Decimal
    lon: Decimal
    tz_id: str
    localtime_epoch: int
    localtime: str


class LocationOut(LocationIn):
    id: int
