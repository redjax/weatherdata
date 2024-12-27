from loguru import logger as log
from dynaconf import Dynaconf

APP_SETTINGS = Dynaconf(
    environments=True,
    env="app",
    envvar_prefix="APP",
    settings_files=["settings.toml", ".secrets.toml"]
)
