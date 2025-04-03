import typing as t

from weather_client.apis.api_openmeteo.client.location import search_location
from weather_client.apis.api_openmeteo.constants import OPENMETEO_FORECAST_URL
from domain.openmeteo.location import LocationIn, LocationOut, MeteoLocationModel
import http_lib
from loguru import logger as log
import httpx

__all__ = ["request_current_weather"]


def request_current_weather(
    location_name: str,
    lat: t.Optional[float],
    lon: t.Optional[float],
    forecast_days: int = 1,
    language: str = "en",
    headers: dict | None = None,
    use_cache: bool = False,
    save_to_db: bool = False,
):
    url: str = OPENMETEO_FORECAST_URL

    if location_name is None or location_name == "":
        if lat is None or lon is None:
            raise ValueError(
                "Missing a location name and/or latitude/longitude coordinates."
            )

    if lat is not None and lon is not None:
        pass

    else:
        log.debug(f"Using location name '{location_name}'.")

        search_result: LocationIn = search_location(
            location_name=location_name, use_cache=True, save_to_db=True
        )

        lat = search_result.latitude
        lon = search_result.longitude

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": [
            "uv_index",
            "uv_index_clear_sky",
            "is_day",
            "sunshine_duration",
            "thunderstorm_probability",
            "rain_probability",
            "snowfall_probability",
            "freezing_rain_probability",
            "ice_pellets_probability",
            "precipitation_probability",
        ],
        "models": "gfs_seamless",
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "is_day",
            "precipitation",
            "rain",
            "showers",
            "snowfall",
            "weather_code",
            "cloud_cover",
            "pressure_msl",
            "surface_pressure",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",
        ],
        "minutely_15": [
            "temperature_2m",
            "precipitation",
            "weather_code",
            "wind_direction_80m",
            "is_day",
            "relative_humidity_2m",
            "rain",
            "wind_gusts_10m",
            "wind_speed_10m",
            "dew_point_2m",
            "snowfall",
            "wind_speed_80m",
            "visibility",
            "apparent_temperature",
            "sunshine_duration",
            "wind_direction_10m",
        ],
        "forecast_days": forecast_days,
        "temperature_unit": "fahrenheit",
    }

    ## Build request object
    req: httpx.Request = httpx.Request("GET", url=url, params=params, headers=headers)

    http_controller = http_lib.get_http_controller(use_cache=use_cache)

    with http_controller as http_ctl:
        res = http_ctl.client.send(req)
        res.raise_for_status()

    if res.status_code == 200:
        log.debug(f"Current weather response: [{res.status_code}: {res.reason_phrase}]")

        decoded: dict = http_lib.decode_response(response=res)
        log.debug(f"Decoded current weather response: {decoded}")
    else:
        log.warning(
            f"Non-200 response requesting current weather for location '{location_name}': [{res.status_code}: {res.reason_phrase}]: {res.text}"
        )

        return
