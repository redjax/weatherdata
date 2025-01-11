from loguru import logger as log

from api.responses import API_RESPONSE_DICT
from settings.api_settings import FASTAPI_SETTINGS
from fastapi import APIRouter

from .healthcheck import router as healthcheck_router
from .weather.weather_router import router as weather_router

prefix: str = "/api/v1"

router: APIRouter = APIRouter(prefix=prefix, responses=API_RESPONSE_DICT)

router.include_router(healthcheck_router)
router.include_router(weather_router)
