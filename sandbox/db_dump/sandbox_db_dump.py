import pymysql
import subprocess
import shutil
from dataclasses import dataclass, field
import argparse
from pathlib import Path
import logging

from settings import DB_SETTINGS

log = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Dump a database to a SQL file")

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--db-host", default="localhost", help="Database host")
    parser.add_argument("--db-port", default=3306, type=int, help="Database port")
    parser.add_argument("--db-username", default="root", help="Database username")
    parser.add_argument("--db-password", default=None, help="Database password")
    parser.add_argument("--db-database", default=None, help="Database name")
    parser.add_argument(
        "--backup-file", default="backup.sql", help="File to save backup to"
    )

    args = parser.parse_args()

    return args


@dataclass
class DbSettings:
    host: str | None = field(default=None)
    port: str | None = field(default=None)
    username: str | None = field(default=None)
    password: str | None = field(default=None, repr=False)
    database: str | None = field(default=None)
    backup_file: str = field(default="backup.sql")


def check_mysqldump_installed():
    log.info("Checking if mysqldump app is installed")
    mysqldump_path = shutil.which("mysqldump")

    if not mysqldump_path:
        log.error(
            "mysqldump is not installed or not in your PATH.\n"
            "Install it using one of the following commands:\n"
            "  Ubuntu/Debian: sudo apt install default-mysql-client\n"
            "  CentOS/RHEL:   sudo yum install mysql\n"
            "  macOS:         brew install mysql\n"
            "Then re-run this script."
        )

        return False

    log.info(f"mysqldump found at: {mysqldump_path}")
    return True


def load_db_settings(
    host: str | None,
    port: str | None,
    username: str | None,
    password: str | None,
    database: str,
    backup_file: str = "backup.sql",
):
    if host is None or host == "":
        raise ValueError("Missing database host")

    if port is None or port == "":
        raise ValueError("Missing database port")

    if username is None or username == "":
        raise ValueError("Missing database username")

    if password is None or password == "":
        raise ValueError("Missing database password")

    if database is None or database == "":
        raise ValueError("Missing database name")

    if backup_file is None or backup_file == "":
        raise ValueError("Missing backup file name")

    db_settings: DbSettings = DbSettings(
        host=host,
        port=port,
        username=username,
        password=password,
        database=database,
        backup_file=backup_file,
    )

    return db_settings


def build_backup_command(
    host: str,
    port: int | str,
    username: str,
    password: str,
    database: str,
    backup_file: str,
):
    command: str = (
        f"mysqldump -h {host} -P {port} -u {username} -p'{password}' {database} > {backup_file}"
    )

    return command


def main(db_settings: DbSettings | dict):
    mysqldump_is_installed = check_mysqldump_installed()
    if not mysqldump_is_installed:
        exit(1)

    if isinstance(db_settings, dict):
        db_settings: DbSettings = DbSettings(**db_settings)
    log.debug(f"DB settings: {db_settings}")

    log.info(
        f"Establishing connection to MySQL database '{db_settings.database}' on host '{db_settings.host}:{db_settings.port}'"
    )
    try:
        ## Establish connection with the MySQL database
        connection = pymysql.connect(
            host=db_settings.host,
            user=db_settings.username,
            password=db_settings.password,
            database=db_settings.database,
        )
    except Exception as exc:
        log.error(f"Error creating pymysql connection. Details: {exc}")
        raise

    ## Build the mysqldump command
    command: str = build_backup_command(**db_settings.__dict__)

    ## Ensure backup file directory exists
    if not Path(db_settings.backup_file).parent.exists():
        try:
            Path(db_settings.backup_file).parent.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            log.error(f"Error creating backup directory: {exc}")
            raise

    log.info(
        f"Running database dump command, backup will be saved to: {db_settings.backup_file}"
    )
    ## Execute the mysqldump command
    try:
        subprocess.run(command, shell=True)
    except Exception as exc:
        log.error(f"Error dumping database: {exc}")
        raise
    finally:
        ## Close the database connection
        connection.close()

    log.info(f"Database '{db_settings.database}' dumped to '{db_settings.backup_file}'")


if __name__ == "__main__":
    args = parse_args()

    if args.debug:
        log_level = "DEBUG"
    else:
        log_level = "INFO"

    if log_level == "DEBUG":
        fmt = "%(asctime)s | [%(levelname)s] | %(name)s:%(lineno)s :: %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
    else:
        fmt = "%(asctime)s [%(levelname)s] :: %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(level=log_level, format=fmt, datefmt=datefmt)
    log.debug("DEBUG logging enabled")

    ## Define database connection details
    host = DB_SETTINGS.get("DB_HOST", "localhost")
    port = DB_SETTINGS.get("DB_PORT", 3306)
    username = DB_SETTINGS.get("DB_USERNAME", None)
    password = DB_SETTINGS.get("DB_PASSWORD", None)
    database = DB_SETTINGS.get("DB_DATABASE", None)
    backup_file = "backup.sql"

    if host is None:
        host = args.db_host
    if port is None:
        host = args.db_port
    if username is None:
        username = args.db_username
    if password is None:
        password = args.db_password
    if database is None:
        database = args.db_database
    if args.backup_file is not None:
        backup_file = args.backup_file

    db_settings: dict = {
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "database": database,
        "backup_file": backup_file,
    }

    main(db_settings=db_settings)
