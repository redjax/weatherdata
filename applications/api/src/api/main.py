import typing as t

from fastapi import FastAPI

from api import utils as api_utils

fastapi_app: FastAPI = api_utils.get_app(debug=..., )

@fastapi_app.get("/")
def read_root():
    return {"Hello": "World"}

