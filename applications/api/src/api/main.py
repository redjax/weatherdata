import typing as t

from fastapi import FastAPI

from api import utils as api_utils
from settings.api_settings import FASTAPI_SETTINGS

fastapi_app: FastAPI = api_utils.get_app(
    debug=FASTAPI_SETTINGS.get("FASTAPI_DEBUG", default=False),
    cors=True,
    root_path=FASTAPI_SETTINGS.get("FASTAPI_ROOT_PATH"),
    title=FASTAPI_SETTINGS.get("FASTAPI_TITLE"),
    description=FASTAPI_SETTINGS.get("FASTAPI_DESCRIPTION"),
    version=FASTAPI_SETTINGS.get("FASTAPI_VERSION"),
    openapi_url=FASTAPI_SETTINGS.get("FASTAPI_OPENAPI_URL"),
)


@fastapi_app.get("/")
def read_root():
    return {"Hello": "World"}
