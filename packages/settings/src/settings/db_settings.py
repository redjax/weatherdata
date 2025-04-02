from __future__ import annotations

from dynaconf import Dynaconf
from settings.base import get_namespace

__all__ = ["DB_SETTINGS"]

## Database settings loaded with dynaconf
# DB_SETTINGS: Dynaconf = Dynaconf(
#     environments=True,
#     envvar_prefix="DB",
#     settings_files=[
#         "settings.toml",
#         ".secrets.toml",
#         "database/settings.toml",
#         "database/.secrets.toml",
#     ],
# )

DB_SETTINGS = get_namespace("database")
