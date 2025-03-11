from settings import OPENMETEO_SETTINGS

__all__ = ["location_name", "location_lat", "location_lon"]

location_name = OPENMETEO_SETTINGS.get("OPENMETEO_LOCATION", default=None)
location_lat = OPENMETEO_SETTINGS.get("OPENMETEO_LAT", default=None)
location_lon = OPENMETEO_SETTINGS.get("OPENMETEO_LON", default=None)