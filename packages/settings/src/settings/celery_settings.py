from __future__ import annotations

from dynaconf import Dynaconf
from loguru import logger as log

__all__ = ["CELERY_SETTINGS"]

## Celery settings loaded with dynaconf
CELERY_SETTINGS: Dynaconf = Dynaconf(
    environments=True,
    envvar_prefix="CELERY",
    settings_files=[
        "settings.toml",
        ".secrets.toml",
        "celery/settings.toml",
        "celery/.secrets.toml",
    ],
)
