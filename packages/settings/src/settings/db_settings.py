from loguru import logger as log
from dynaconf import Dynaconf

## Database settings loaded with dynaconf
DB_SETTINGS: Dynaconf = Dynaconf(
    environments=True,
    env="database",
    envvar_prefix="DB",
    settings_files=["database/settings.toml", "database/.secrets.toml"],
)
