import typing as t

from weather_client.apis.api_openmeteo.convert import (
    location_search_result_dicts_to_schema,
)

import http_lib
from weather_client.apis import api_openmeteo
from domain.openmeteo import location as openmeteo_location_domain

from loguru import logger as log
import httpx

__all__ = ["search_location"]


def search_location(
    location_name: str,
    results_limit: int = 1,
    language: str = "en",
    headers: dict | None = None,
    use_cache: bool = False,
    save_to_db: bool = False,
) -> t.Union[
    openmeteo_location_domain.LocationIn, list[openmeteo_location_domain.LocationIn]
]:
    """Request a location from OpenMeteo.

    Params:
        location_name (str): The name of the location to request.
        results_limit (int): The maximum number of results to return.
        language (str): The language to use for the response.

    Returns:
        (LocationIn): If a single location was found
        (list[LocationIn]): A list of objects if multiple locations were found.

    """
    url = f"{api_openmeteo.OPENMETEO_GEOCODING_BASE_URL}"
    params = {
        "name": location_name,
        "count": results_limit,
        "language": language,
        "format": "json",
    }

    req: httpx.Request = http_lib.build_request(url=url, params=params, headers=headers)

    http_controller = http_lib.get_http_controller(use_cache=use_cache)

    with http_controller as http_ctl:
        res = http_ctl.client.send(req)
        res.raise_for_status()

    if res.status_code == 200:
        log.debug(f"Location response: [{res.status_code}: {res.reason_phrase}]")

        decoded: dict = http_lib.decode_response(response=res)
        # log.debug(f"Decoded location response: {decoded}")
    else:
        log.warning(
            f"Non-200 response requesting location '{location_name}': [{res.status_code}: {res.reason_phrase}]: {res.text}"
        )

    search_result_schemas: (
        list[openmeteo_location_domain.LocationIn]
        | openmeteo_location_domain.LocationIn
    ) = location_search_result_dicts_to_schema(decoded["results"])

    if isinstance(search_result_schemas, list):
        if len(search_result_schemas) == 1:
            log.debug(f"Found a single location")
            location_schema: openmeteo_location_domain.LocationIn = (
                search_result_schemas[0]
            )

            if save_to_db:
                log.warning(
                    "Saving OpenMeteo location to database is not implemented yet"
                )

            return location_schema

        else:
            log.debug(
                f"Found [{len(search_result_schemas)}] {'locations' if (len(search_result_schemas) > 1 or len(search_result_schemas) == 0) else 'location'}"
            )

            if save_to_db:
                log.warning(
                    "Saving OpenMeteo locations to database is not implemented yet"
                )

            return search_result_schemas

    else:
        return search_result_schemas
