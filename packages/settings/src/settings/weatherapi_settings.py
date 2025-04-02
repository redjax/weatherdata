from __future__ import annotations

from dynaconf import Dynaconf
from settings.base import get_namespace

__all__ = ["WEATHERAPI_SETTINGS"]

# WEATHERAPI_SETTINGS = Dynaconf(
#     environments=True,
#     envvar_prefix="WEATHERAPI",
#     settings_files=[
#         "settings.toml",
#         ".secrets.toml",
#         "weatherapi/settings.toml",
#         "weatherapi/.secrets.toml",
#     ],
# )

WEATHERAPI_SETTINGS = get_namespace("weatherapi")
