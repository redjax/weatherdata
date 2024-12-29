from __future__ import annotations

from dynaconf import Dynaconf
import pika

from loguru import logger as log

## Dramatiq settings loaded with dynaconf
DRAMATIQ_SETTINGS: Dynaconf = Dynaconf(
    environments=True,
    env="dramatiq",
    envvar_prefix="DRAMATIQ",
    settings_files=["dramatiq/settings.toml", "dramatiq/.secrets.toml"],
)


def return_dramatiq_rabbitmq_url(
    username: str = DRAMATIQ_SETTINGS.get("DRAMATIQ_RABBITMQ_USERNAME", default="guest"),
    password: str = DRAMATIQ_SETTINGS.get("DRAMATIQ_RABBITMQ_PASSWORD", default=""),
    host: str = DRAMATIQ_SETTINGS.get("DRAMATIQ_RABBITMQ_HOST", default="localhost"),
    port: str = DRAMATIQ_SETTINGS.get("DRAMATIQ_RABBITMQ_PORT", default=5672),
):
    """Return a string of the format amqp://<username>:<password>@<host>:<port> for RabbitMQ.
    
    Params:
        username (str): The username for database auth.
        password (str): The password for database auth.
        host (str): The host for database auth.
        port (str): The port for database auth.
    """
    dramatiq_broker_url: str = f"amqp://{username}:{password}@{host}:{port}"
    log.debug(f"Dramatiq broker URL: {dramatiq_broker_url}")
    
    return dramatiq_broker_url


def return_dramatiq_rabbitmq_credentials(username: str = DRAMATIQ_SETTINGS.get("DRAMATIQ_RABBITMQ_USERNAME", default="guest"), password: str = DRAMATIQ_SETTINGS.get("DRAMATIQ_RABBITMQ_PASSWORD", default="")):
    """Return a pika.PlainCredentials object for use with RabbitMQ.
    
    Params:
        username (str): The username for database auth.
        password (str): The password for database auth.
        
    Returns:
        pika.PlainCredentials
    """
    return pika.PlainCredentials(username, password)
