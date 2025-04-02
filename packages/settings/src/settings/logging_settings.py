from __future__ import annotations

from dynaconf import Dynaconf
from settings.base import get_namespace

__all__ = ["LOGGING_SETTINGS"]

# LOGGING_SETTINGS = Dynaconf(
#     environments=True,
#     envvar_prefix="LOG",
#     settings_files=[
#         "settings.toml",
#         ".secrets.toml",
#         "logging/settings.toml",
#         "logging/.secrets.toml",
#     ],
# )

LOGGING_SETTINGS = get_namespace("logging")
