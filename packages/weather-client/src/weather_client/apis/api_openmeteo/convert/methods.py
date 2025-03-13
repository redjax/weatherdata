import typing as t

from domain.openmeteo import location as openmeteo_location_domain

from loguru import logger as log

__all__ = ["location_search_result_dicts_to_schema"]


def location_search_result_dicts_to_schema(
    search_results: list[dict],
) -> openmeteo_location_domain.LocationIn | list[openmeteo_location_domain.LocationIn]:

    location_schemas: list[dict] = []

    if len(search_results) == 1:
        log.debug(f"Found a single location")
        location_dict: dict = search_results[0]

        try:
            location_schema: openmeteo_location_domain.LocationIn = (
                openmeteo_location_domain.LocationIn.model_validate(location_dict)
            )
        except Exception as exc:
            msg = f"({type(exc)}) Error converting location dict to LocationIn schema. Details: {exc}"
            log.error(msg)

            raise

        return location_schema

    else:
        log.debug(
            f"Found [{len(search_results)}] {'locations' if (len(search_results) > 1 or len(search_results) == 0) else 'location'}"
        )

        for location_dict in search_results:
            try:
                location_schema: openmeteo_location_domain.LocationIn = (
                    openmeteo_location_domain.LocationIn.model_validate(location_dict)
                )
                location_schemas.append(location_schema)
            except Exception as exc:
                msg = f"({type(exc)}) Error converting location dict to LocationIn schema. Details: {exc}"
                log.error(msg)

                continue

        log.debug(
            f"Converted [{len(location_schemas)}/{len(search_results)}] location search response dict(s) to LocationIn"
        )

        return location_schemas
