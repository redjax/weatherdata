from __future__ import annotations

from settings import WEATHERAPI_SETTINGS

api_key: str = WEATHERAPI_SETTINGS.get("WEATHERAPI_API_KEY", default=None)
location_name: str = WEATHERAPI_SETTINGS.get("WEATHERAPI_LOCATION_NAME", default=None)