import typing as t

from api import helpers as api_helpers
from api.responses import API_RESPONSE_DICT, img_response
from celery.result import AsyncResult

from scheduling.celery_scheduler import celeryapp
from fastapi import APIRouter, Depends, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse

from . import current_weather_router, weather_forecast_router

from loguru import logger as log

prefix: str = "/weather"
tags: list[str] = ["weather", "weatherapi"]

router: APIRouter = APIRouter(prefix=prefix, responses=API_RESPONSE_DICT, tags=tags)
router.include_router(current_weather_router.router)
router.include_router(weather_forecast_router.router)
