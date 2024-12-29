from scheduling.demo_tasks.tasks import count_words
from loguru import logger as log

import depends
import setup
from settings.logging_settings import LOGGING_SETTINGS
from settings.dramatiq_settings import DRAMATIQ_SETTINGS
from dramatiq.brokers.rabbitmq import RabbitmqBroker

dramatiq_rabbitmq_settings = {
    "host": DRAMATIQ_SETTINGS.get("DRAMATIQ_RABBITMQ_HOST", default="localhost"),
    "port": DRAMATIQ_SETTINGS.get("DRAMATIQ_RABBITMQ_PORT", default=5672),
    "user": DRAMATIQ_SETTINGS.get("DRAMATIQ_RABBITMQ_USERNAME", default="guest"),
    "password": DRAMATIQ_SETTINGS.get("DRAMATIQ_RABBITMQ_PASSWORD", default=""),
}

dramatiq_broker_url = f"amqp://{dramatiq_rabbitmq_settings['user']}:{dramatiq_rabbitmq_settings['password']}@{dramatiq_rabbitmq_settings['host']}:{dramatiq_rabbitmq_settings['port']}"

demo_db_dict = {"drivername": "sqlite+pysqlite", "username": None, "password": None, "host": None, "port": None, "database": ".db/demo.sqlite3"}

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    
    ## Create a demo.sqlite3 database separate from app's database
    demo_db_uri = depends.get_db_uri(**demo_db_dict)
    setup.setup_database(engine=depends.get_db_engine(db_uri=demo_db_uri))
    
    rabbitmq_broker = RabbitmqBroker(url=dramatiq_broker_url)
    
    log.debug(f"Dramatiq RabbitMQ settings: {dramatiq_rabbitmq_settings}")
    log.debug(f"Dramatiq broker URL: {dramatiq_broker_url}")
    
    count_words.send("https://www.xkcd.com")
