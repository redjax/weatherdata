from __future__ import annotations

import typing as t

from cyclopts import App, Group, Parameter
from depends import db_depends
from loguru import logger as log
import settings
import setup
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.sql as sa_sql

__all__ = ["db_app"]

db_app = App(name="db", help="CLI for managing the database.")


@db_app.command(name="init")
def _init_db():
    """Initialize the database."""
    log.info("Initializing database.")

    engine = db_depends.get_db_engine()
    log.debug(f"DB engine URL: {engine.url}")

    try:
        setup.setup_database(engine=engine)
        log.success("Database initialized.")
    except Exception as exc:
        msg = f"({type(exc)}) Error initializing database. Details: {exc}"
        log.error(msg)

        raise exc


@db_app.command(name="show")
def show_db_info(
    option: t.Annotated[
        str,
        Parameter(
            name="option", show_default=True, help="Options: ['tables', 'driver']"
        ),
    ],
):
    """Show information about the database.

    Params:
        option: The option to show information about. Options: ['tables', 'driver']

    """
    log.info(f"Showing database info: {option}")

    engine = db_depends.get_db_engine()

    match option.lower():
        case "table" | "tables":
            log.info("Showing database tables")

            try:
                inspector = sa.inspect(engine)
                tables: list[str] = inspector.get_table_names()

                if tables:
                    log.debug(f"Tables in the database: {tables}")

                    print(f"Tables [{len(tables)}]:")
                    for table in tables:
                        print(f" - {table}")

                    return tables
                else:
                    log.warning("No tables found in the database.")
                    return
            except sa_exc.SQLAlchemyError as e:
                print(f"Error inspecting database: {e}")

        case "driver":
            inspector = sa.inspect(engine)

            url = engine.url

            print(f"Database type: {url.get_backend_name().title()}")
            print(f"Driver: {url.get_driver_name().title()}")
            print(f"Database URL: {url}")

            if url.host:
                print(f"Host: {url.host}")
            if url.port:
                print(f"Port: {url.port}")
            if url.database:
                print(f"Database: {url.database}")
            if url.username:
                print(f"Username: {url.username}")

        case _:
            log.error(f"Unknown option: {option}")
            exit(1)


@db_app.command(name="count")
def count_db_rows(table: t.Annotated[str, Parameter(name="table", show_default=True)]):
    """Count the number of rows in a table.

    Params:
        table: The table to count the rows in.

    Returns:
        int: The number of rows in the table.

    """
    log.info(f"Counting rows in table: {table}")

    engine = db_depends.get_db_engine()
    session_pool = db_depends.get_session_pool(engine=engine)

    ## Count number of rows in given table name
    with session_pool() as session:
        if not sa.inspect(engine).has_table(table):
            log.error(f"Table '{table}' does not exist.")
            return

        query = sa_sql.text(f"SELECT COUNT(*) FROM {table}")
        try:
            count = session.execute(query).scalar()
        except Exception as exc:
            msg = (
                f"({type(exc)}) Error counting rows in table '{table}'. Details: {exc}"
            )
            log.error(msg)

            raise exc
        except sa_exc.SQLAlchemyError as exc:
            log.error(f"Error querying table '{table}': {exc}")

        log.success(f"[{count}] row(s) in table '{table}'.")


@db_app.command(name="test-connection")
def test_db_connection():
    log.info("Testing database connection")
    log.debug(f"Database settings: {settings.DB_SETTINGS.as_dict()}")

    session_pool = db_depends.get_session_pool()

    try:
        with session_pool() as session:
            result = session.execute(sa.text("SELECT 1")).scalar()
            if result == 1:
                log.success(f"Database connection successful.")
            else:
                log.warning(
                    "Success connecting to database, but test query returned an unexpected result."
                )
    except Exception as exc:
        msg = f"({type(exc)}) Error connecting to database: {exc}"
        log.error(msg)

        return False
