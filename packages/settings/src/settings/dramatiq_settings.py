from __future__ import annotations

from dynaconf import Dynaconf
from loguru import logger as log

## Dramatiq settings loaded with dynaconf
DRAMATIQ_SETTINGS: Dynaconf = Dynaconf(
    environments=True,
    env="dramatiq",
    envvar_prefix="DRAMATIQ",
    settings_files=["dramatiq/settings.toml", "dramatiq/.secrets.toml"],
)
