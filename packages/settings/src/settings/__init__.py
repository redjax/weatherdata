from __future__ import annotations

from .api_settings import FASTAPI_SETTINGS, UVICORN_SETTINGS
from .app_settings import APP_SETTINGS
from .celery_settings import CELERY_SETTINGS
from .db_settings import DB_SETTINGS
from .dramatiq_settings import (
    DRAMATIQ_SETTINGS,
    return_dramatiq_rabbitmq_credentials,
    return_dramatiq_rabbitmq_url,
)
from .logging_settings import LOGGING_SETTINGS
from .weatherapi_settings import WEATHERAPI_SETTINGS
