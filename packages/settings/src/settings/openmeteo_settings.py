from __future__ import annotations

from dynaconf import Dynaconf
from loguru import logger as log

__all__ = ["OPENMETEO_SETTINGS"]

OPENMETEO_SETTINGS = Dynaconf(
    environments=True,
    envvar_prefix="OPENMETEO",
    settings_files=[
        "settings.toml",
        ".secrets..toml",
        "openmeteo/settings.toml",
        "openmeteo/.secrets.toml",
    ],
)
