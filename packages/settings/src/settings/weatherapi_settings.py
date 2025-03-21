from __future__ import annotations

from dynaconf import Dynaconf
from loguru import logger as log

__all__ = ["WEATHERAPI_SETTINGS"]

WEATHERAPI_SETTINGS = Dynaconf(
    environments=True,
    envvar_prefix="WEATHERAPI",
    settings_files=["weatherapi/settings.toml", "weatherapi/.secrets.toml"]
)