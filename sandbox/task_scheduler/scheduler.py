from __future__ import annotations

import depends
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from loguru import logger as log
import pika
from scheduling.demo_tasks.tasks import count_words
from settings.dramatiq_settings import (
    DRAMATIQ_SETTINGS,
    return_dramatiq_rabbitmq_credentials,
    return_dramatiq_rabbitmq_url,
)
from settings.logging_settings import LOGGING_SETTINGS
import setup

dramatiq_rabbitmq_settings = {
    "host": DRAMATIQ_SETTINGS.get("DRAMATIQ_RABBITMQ_HOST", default="localhost"),
    "port": DRAMATIQ_SETTINGS.get("DRAMATIQ_RABBITMQ_PORT", default=5672),
    # "user": DRAMATIQ_SETTINGS.get("DRAMATIQ_RABBITMQ_USERNAME", default="guest"),
    # "password": DRAMATIQ_SETTINGS.get("DRAMATIQ_RABBITMQ_PASSWORD", default=""),
    "credentials": pika.PlainCredentials(
        DRAMATIQ_SETTINGS.get("DRAMATIQ_RABBITMQ_USERNAME", default="guest"),
        DRAMATIQ_SETTINGS.get("DRAMATIQ_RABBITMQ_PASSWORD", default="")
    )
}

demo_db_dict = {"drivername": "sqlite+pysqlite", "username": None, "password": None, "host": None, "port": None, "database": ".db/demo.sqlite3"}


def test_rabbitmq_connection(username: str = "rabbitmq", password: str = "rabbitmq", host: str = "localhost", port: int = 5672, vhost: str = "rabbitmq") -> bool:
    ## Test connection with pika
    credentials = pika.PlainCredentials(username, password)
    parameters = pika.ConnectionParameters(host, port, vhost, credentials)
    
    log.debug(f"""
RabbitMQ Connection Test
Username: {username}
Password: {password}
VHOST: {vhost}
""")

    try:
        connection = pika.BlockingConnection(parameters)
        log.success("Connection successful!")
        
        return True
    except Exception as e:
        log.error(f"Connection failed: {e}")
        
        return False

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    
    ## Create a demo.sqlite3 database separate from app's database
    demo_db_uri = depends.get_db_uri(**demo_db_dict)
    setup.setup_database(engine=depends.get_db_engine(db_uri=demo_db_uri))
    
    if not test_rabbitmq_connection(username=DRAMATIQ_SETTINGS.DRAMATIQ_RABBITMQ_USERNAME, password=DRAMATIQ_SETTINGS.DRAMATIQ_RABBITMQ_PASSWORD, vhost=DRAMATIQ_SETTINGS.DRAMATIQ_RABBITMQ_VHOST):
        raise Exception("RabbitMQ connection test failed")
    
    log.debug(f"Dramtiq Settings: {DRAMATIQ_SETTINGS.as_dict()}")
    # log.debug(f"Username: {DRAMATIQ_SETTINGS.DRAMATIQ_RABBITMQ_USERNAME}")
    # log.debug(f"Password: {DRAMATIQ_SETTINGS.DRAMATIQ_RABBITMQ_PASSWORD}")
    # log.debug(f"VHOST: {DRAMATIQ_SETTINGS.DRAMATIQ_RABBITMQ_VHOST}")
    
    # log.debug(f"Test dramatiq rabbitmq URL: {return_dramatiq_rabbitmq_url()}")
    # log.debug(f"Test dramatiq rabbitmq pika credentials: {return_dramatiq_rabbitmq_credentials()}")
    
    dramatiq_broker_url = return_dramatiq_rabbitmq_url()
    
    # log.debug(f"Dramatiq RabbitMQ settings: {dramatiq_rabbitmq_settings}")
    log.debug(f"Dramatiq broker URL: {dramatiq_broker_url}")
    
    # rabbitmq_broker = RabbitmqBroker(**dramatiq_rabbitmq_settings)
    rabbitmq_broker = RabbitmqBroker(host=DRAMATIQ_SETTINGS.DRAMATIQ_RABBITMQ_HOST, port=DRAMATIQ_SETTINGS.DRAMATIQ_RABBITMQ_PORT, credentials=return_dramatiq_rabbitmq_credentials())
    
    try:
        count_words.send("https://www.xkcd.com")
    except Exception as exc:
        msg = f"({type(exc)}) Unhandled exception counting words at https://www.xkcd.com. Details: {exc}"
        log.error(msg)
        
        raise exc