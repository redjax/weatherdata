import typing as t
from cyclopts import App, Group, Parameter
from loguru import logger as log

import setup
from depends import db_depends
from weather_client.apis import api_weatherapi
import settings

db_app = App(name="db", help="CLI for managing the database.")


@db_app.command(name="init")
def _init_db():
    """Initialize the database."""
    log.info("Initializing database.")
    
    try:
        setup.setup_database()
        log.success("Database initialized.")
    except Exception as exc:
        msg = f"({type(exc)}) Error initializing database. Details: {exc}"
        log.error(msg)
        
        raise exc