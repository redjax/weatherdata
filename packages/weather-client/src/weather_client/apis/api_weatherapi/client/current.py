from __future__ import annotations

import time

from weather_client.apis.api_weatherapi.constants import WEATHERAPI_BASE_URL
from weather_client.apis.api_weatherapi.settings import api_key, location_name
from weather_client.apis.api_weatherapi.db_client.current_weather import save_current_weather
from weather_client.apis.api_weatherapi.convert.methods import current_weather_dict_to_schema, location_dict_to_schema
from depends import db_depends
from . import requests

import hishel
import http_lib
import httpx
from loguru import logger as log

import sqlalchemy as sa
import sqlalchemy.orm as so
import sqlalchemy.exc as sa_exc

def get_current_weather(
    location: str = location_name,
    api_key: str = api_key,
    include_aqi: bool = True,
    headers: dict | None = None,
    use_cache: bool = False,
    retry: bool = True,
    max_retries: int = 3,
    retry_sleep: int = 5,
    retry_stagger: int = 3,
    save_to_db: bool = False,
    db_engine: sa.Engine | None = None,
    db_echo: bool = False
) -> dict | None:
    current_weather_request: httpx.Request = requests.return_current_weather_request(
        api_key=api_key, location=location, include_aqi=include_aqi, headers=headers
    )
    
    log.info("Requesting current weather")

    with http_lib.get_http_controller(use_cache=use_cache) as http:
        try:
            res: httpx.Response = http.client.send(current_weather_request)
        except httpx.ReadTimeout as timeout:
            log.warning(
                f"({type(timeout)}) Operation timed out while requesting current weather."
            )

            if not retry:
                raise timeout
            else:
                log.info(f"Retrying {max_retries} time(s)")
                current_attempt = 0
                _sleep = retry_sleep

                while current_attempt < max_retries:
                    if current_attempt > 0:
                        _sleep += retry_stagger

                    log.info(f"[Retry {current_attempt}/{max_retries}]")

                    try:
                        res: httpx.Response = http.client.send(current_weather_request)
                        break
                    except httpx.ReadTimeout as timeout_2:
                        log.warning(
                            f"ReadTimeout on attempt [{current_attempt}/{max_retries}]"
                        )

                        current_attempt += 1

                        time.sleep(retry_sleep)

                        continue

    log.debug(f"Response: [{res.status_code}: {res.reason_phrase}]")

    if res.status_code in http_lib.constants.SUCCESS_CODES:
        log.info("Success requesting current weather")
        decoded = http_lib.decode_response(response=res)
    elif res.status_code in http_lib.constants.ALL_ERROR_CODES:
        log.warning(f"Error: [{res.status_code}: {res.reason_phrase}]: {res.text}")

        return None
    else:
        log.error(
            f"Unhandled error code: [{res.status_code}: {res.reason_phrase}]: {res.text}"
        )

        return None
    
    if save_to_db:
        if not db_engine:
            db_engine = db_depends.get_db_engine()

        # log.warning("Saving current weather to database is not implemented")
        errored: bool = False
        
        try:
            db_location_in = location_dict_to_schema(location_dict=decoded["location"])
        except Exception as exc:
            msg = f"({type(exc)}) Error converting decoded response to schema. Details: {exc}"
            log.error(msg)
            
            errored = True
        
        if not errored:
            try:
                db_current_weather_in = current_weather_dict_to_schema(
                    current_weather_dict=decoded["current"]
                )
            except Exception as exc:
                msg = f"({type(exc)}) Error converting decoded response to schema. Details: {exc}"
                log.error(msg)
                
                errored = True
                
        if not errored:
            ## Save current weather to database
            try:
                db_current_weather_out = save_current_weather(
                    current_weather=db_current_weather_in, engine=db_engine, echo=db_echo
                )
                log.success("Saved current weather to database")
                log.debug(f"Current weather from database: {db_current_weather_out}")
            except Exception as exc:
                msg= f"({type(exc)}) Error saving current weather to database: {exc}"
                log.error(msg)
                
                errored = True
                
        if errored:
            log.warning("Errored while saving current weather and/or location to database.")

    return decoded
