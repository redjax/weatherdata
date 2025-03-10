from __future__ import annotations

import typing as t

from api import helpers as api_helpers
from api.responses import API_RESPONSE_DICT, img_response
from celery.result import AsyncResult
from domain.weatherapi.location import LocationIn, LocationOut
from domain.weatherapi.weather.current import CurrentWeatherIn, CurrentWeatherOut
from fastapi import APIRouter, Depends, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from loguru import logger as log
from scheduling.celery_scheduler import celeryapp
from weather_client.apis import api_weatherapi

__all__ = ["router"]

prefix: str = "/current"
tags: list[str] = ["weather", "weatherapi", "current"]

router: APIRouter = APIRouter(prefix=prefix, responses=API_RESPONSE_DICT, tags=tags)

@router.get("/{location}")
def get_current_weather_for_location(location: str) -> t.Union[CurrentWeatherIn, CurrentWeatherOut]:
    log.info(f"Requesting current weather from WeatherAPI for location: {location}")
    try:
        current_weather_dict = api_weatherapi.client.get_current_weather(location=location)
    except Exception as exc:
        msg = f"({type(exc)}) Error requesting current weather. Details: {exc}"
        log.error(msg)
        
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"text": f"Error requesting current weather for location: {location}. Errored while making request to WeatherAPI."})
    
    try:
        current_weather: CurrentWeatherIn = CurrentWeatherIn.model_validate(current_weather_dict["current"])
    except Exception as exc:
        msg = f"({type(exc)}) Error converting WeatherAPI current weather response to CurrentWeatherIn domain object. Details: {exc}"
        log.error(msg)
        
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"text": f"Error requesting current weather for location: {location}. Errored while converting WeatherAPI response to CurrentWeatherIn object."})
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            # "current_weather": current_weather.model_dump()
            "location": current_weather_dict["location"],
            "current_weather": current_weather_dict["current"],
        }
    )
