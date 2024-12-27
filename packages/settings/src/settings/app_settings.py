from __future__ import annotations

from dynaconf import Dynaconf
from loguru import logger as log

APP_SETTINGS = Dynaconf(
    environments=True,
    env="app",
    envvar_prefix="APP",
    settings_files=["settings.toml", ".secrets.toml"]
)
