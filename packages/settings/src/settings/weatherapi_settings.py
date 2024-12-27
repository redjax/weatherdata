from loguru import logger as log
from dynaconf import Dynaconf

WEATHERAPI_SETTINGS = Dynaconf(
    environments=True,
    env="weatherapi",
    envvar_prefix="WEATHERAPI",
    settings_files=["weatherapi/settings.toml", "weatherapi/.secrets.toml"]
)