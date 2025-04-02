from __future__ import annotations

from dynaconf import Dynaconf
from settings.base import get_namespace

__all__ = ["APP_SETTINGS"]

# APP_SETTINGS = Dynaconf(
#     environments=True,
#     envvar_prefix="APP",
#     settings_files=["settings.toml", ".secrets.toml"]
# )

APP_SETTINGS = get_namespace("app")
