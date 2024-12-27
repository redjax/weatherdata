from __future__ import annotations

import datetime as dt
import typing as t

from loguru import logger as log
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

class ForecastJSONIn(BaseModel):
    forecast_json: dict


class ForecastJSONOut(ForecastJSONIn):
    id: int

    created_at: dt.datetime