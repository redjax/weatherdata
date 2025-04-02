from __future__ import annotations

from dynaconf import Dynaconf

__all__ = ["FASTAPI_SETTINGS", "UVICORN_SETTINGS"]

FASTAPI_SETTINGS = Dynaconf(
    environments=True,
    envvar_prefix="FASTAPI",
    settings_files=[
        "settings.toml",
        ".secrets.toml",
        "fastapi/settings.toml",
        "fastapi/.secrets.toml",
    ],
)

UVICORN_SETTINGS = Dynaconf(
    environments=True,
    envvar_prefix="UVICORN",
    settings_files=[
        "settings.toml",
        ".secrets.toml",
        "uvicorn/settings.toml",
        "uvicorn/.secrets.toml",
    ],
)
