from __future__ import annotations

import json
import typing as t

from weather_client.apis.api_weatherapi.db_client.location import save_location

import db
from depends import db_depends
from domain.weatherapi import location as domain_location
from domain.weatherapi.weather import current as domain_current_weather
from loguru import logger as log
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so

def save_current_weather(
    location: t.Union[domain_location.LocationIn, dict, str], current_weather: t.Union[domain_current_weather.CurrentWeatherIn, dict, str], engine: sa.Engine | None = None, echo: bool = False
) -> domain_current_weather.CurrentWeatherOut | None:
    if not current_weather:
        raise ValueError("Missing current weather to save")

    if isinstance(current_weather, str):
        try:
            current_weather: dict = json.loads(current_weather)
        except Exception as exc:
            msg = f"({type(exc)}) Error parsing current weather string as JSON. Details: {exc}"
            log.error(msg)

            raise exc

    if isinstance(current_weather, dict):
        try:
            current_weather: domain_current_weather.CurrentWeatherIn = domain_current_weather.CurrentWeatherIn.model_validate(current_weather)
        except Exception as exc:
            msg = f"({type(exc)}) Error parsing current weather dict as CurrentWeatherIn domain object. Details: {exc}"
            log.error(msg)

            raise exc

    if not location:
        raise ValueError("Missing location to save current weather to")
    
    if isinstance(location, str):
        try:
            location: dict = json.loads(location)
        except Exception as exc:
            msg = f"({type(exc)}) Error parsing location string as JSON. Details: {exc}"
            log.error(msg)

            raise exc

    if isinstance(location, dict):
        try:
            location: domain_location.LocationIn = domain_location.LocationIn.model_validate(location)
        except Exception as exc:
            msg = f"({type(exc)}) Error parsing location dict as LocationIn domain object. Details: {exc}"
            log.error(msg)

            raise exc

    ## Build special schemas
    condition_schema: domain_current_weather.CurrentWeatherConditionIn = current_weather.condition
    air_quality_schema: domain_current_weather.CurrentWeatherAirQualityIn = current_weather.air_quality

    if engine is None:
        engine = db_depends.get_db_engine(echo=echo)
    
    session_pool = db_depends.get_session_pool(engine=engine)

    with session_pool() as session:
        repo = domain_current_weather.CurrentWeatherRepository(session=session)
        location_repo = domain_location.LocationRepository(session=session)

        try:
            db_location: domain_location.LocationModel = save_location(location=location, engine=engine, echo=echo)
        except Exception as exc:
            msg = f"({type(exc)}) Error saving location. Details: {exc}"
            log.error(msg)

            raise exc
        
        if db_location is None:
            log.warning("Location database transaction returned None.")
            return None
        else:
            log.info("Converting location database model to API schema")
            location_schema: domain_location.LocationOut = domain_location.LocationOut.model_validate(db_location)

        existing_current_weather_model: domain_current_weather.CurrentWeatherModel | None = repo.get_by_last_updated_epoch(
            last_updated_epoch=current_weather.last_updated_epoch
        )

        if existing_current_weather_model:
            log.info(
                f"Last updated time has not changed between current weather requests. Returning existing database entity."
            )

            db_model = existing_current_weather_model

        else:
            log.info("Did not find recent current weather in database. Adding reading.")
            weather_dict: dict = current_weather.model_dump(
                exclude=["air_quality", "condition"]
            )
            weather_dict["location_id"] = location_schema.id
            condition_dict: dict = condition_schema.model_dump()
            air_quality_dict: dict = air_quality_schema.model_dump()

            try:
                db_model: domain_current_weather.CurrentWeatherModel = repo.create_with_related(
                    weather_data=weather_dict,
                    condition_data=condition_dict,
                    air_quality_data=air_quality_dict,
                )
            except Exception as exc:
                msg = f"({type(exc)}) Error adding current weather to database. Details: {exc}"
                log.error(msg)

                raise exc

        if db_model is None:
            log.warning("Current weather database transaction returned None.")
            return None
        else:
            log.info("Converting database model to API schema")

            # Eager load related models
            weather_model = repo.get_with_related(id=db_model.id)

            if weather_model is None:
                log.error(f"Could not find weather entity by ID [{db_model.id}].")
                return None

            try:
                current_weather_schema: domain_current_weather.CurrentWeatherOut = (
                    domain_current_weather.CurrentWeatherOut.model_validate(
                        {
                            **weather_model.__dict__,
                            "condition": weather_model.condition.__dict__,
                            "air_quality": weather_model.air_quality.__dict__,
                        }
                    )
                )

                return current_weather_schema
            except Exception as exc:
                msg = f"({type(exc)}) Error converting current weather database model to API schema. Details: {exc}"
                log.error(msg)

                raise exc

