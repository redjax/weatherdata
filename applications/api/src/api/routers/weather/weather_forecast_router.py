import typing as t

from api import helpers as api_helpers
from api.responses import API_RESPONSE_DICT, img_response
from celery.result import AsyncResult

from scheduling.celery_scheduler import celeryapp
from fastapi import APIRouter, Depends, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from domain.weatherapi.location import LocationIn, LocationOut
from domain.weatherapi.weather.forecast import ForecastJSONIn, ForecastJSONOut
from loguru import logger as log

from weather_client.apis import api_weatherapi

prefix: str = "/forecast"
tags: list[str] = ["weather", "weatherapi", "forecast"]

router: APIRouter = APIRouter(prefix=prefix, responses=API_RESPONSE_DICT, tags=tags)

@router.get("/{location}")
def get_weather_forecast_for_location(location: str, days: int = 1) -> t.Union[ForecastJSONIn, ForecastJSONOut]:
    log.info(f"Requesting weather forecast from WeatherAPI for location: {location}")
    try:
        weather_forecast_dict = api_weatherapi.client.get_weather_forecast(location=location, days=days)
        log.success(f"Retrieved weather forecast from WeatherAPI")
    except Exception as exc:
        msg = f"({type(exc)}) Error requesting weather forecast. Details: {exc}"
        log.error(msg)
        
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"text": f"Error requesting weather forecast for location: {location}. Errored while making request to WeatherAPI."})
    
    try:
        weather_forecast: ForecastJSONIn = ForecastJSONIn(forecast_json=weather_forecast_dict)
    except Exception as exc:
        msg = f"({type(exc)}) Error converting WeatherAPI weather forecast response to ForecastJSONIn domain object. Details: {exc}"
        log.error(msg)
        
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"text": f"Error requesting weather forecast for location: {location}. Errored while converting WeatherAPI response to ForecastJSONIn object."})
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            # "weather_forecast": weather_forecast.model_dump()
            "location": weather_forecast_dict["location"],
            "weather_forecast": weather_forecast_dict["current"],
        }
    )
