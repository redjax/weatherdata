from __future__ import annotations

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pymysql",
# ]
# ///

"""Dump a MySQL database to a SQL file.

Description:
    Wraps the `mysqldump` command to dump a MySQL database to a SQL file. Includes a CLI, run with `--help` to see usage.

Usage:
    python dump_mysql_db.py --db-host <host> --db-port <port> --db-username <username> --db-password <password> --db-database <database> --backup-file <file>

Example:
    python dump_mysql_db.py --db-host localhost --db-port 3306 --db-username root --db-password password --db-database my_database --backup-file backup.sql

"""

import argparse
from dataclasses import dataclass, field
import datetime as dt
import json
import logging
import os
from pathlib import Path
import shutil
import subprocess
import typing as t

import pymysql

log = logging.getLogger(__name__)


__all__ = [
    "start_cli",
    "check_mysqldump_installed",
    "get_default_backup_filename",
    "DbSettings",
    "DatabaseBackupController",
]

## Load database settings from environment variables.
DB_SETTINGS = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", 3306),
    "username": os.environ.get("DB_USERNAME", "root"),
    "password": os.environ.get("DB_PASSWORD", None),
    "database": os.environ.get("DB_DATABASE", None),
    "backup_file": os.environ.get("BACKUP_FILE", "backup.sql"),
}


def parse_args():
    parser = argparse.ArgumentParser(description="Dump a database to a SQL file")

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--generate-config-file",
        action="store_true",
        help="Generate a config JSON file. After editing, pass it into the CLI with `--config-file`",
    )
    parser.add_argument(
        "--config-file",
        default="mysql_dump_config.json",
        help="Define app settings in a config JSON file.",
    )
    parser.add_argument("--db-host", default="localhost", help="Database host")
    parser.add_argument("--db-port", default=3306, type=int, help="Database port")
    parser.add_argument("--db-username", default="root", help="Database username")
    parser.add_argument("--db-password", default=None, help="Database password")
    parser.add_argument("--db-database", default=None, help="Database name")
    parser.add_argument("--backup-file", default=None, help="File to save backup to")

    args = parser.parse_args()

    return args


def check_mysqldump_installed() -> bool:
    """Verify mysqldump installation."""
    log.info("Checking mysqldump installation")

    ## Test if mysqldump is installed
    if path := shutil.which("mysqldump"):
        log.debug(f"mysqldump found at: {path}")
        return True

    log.error(
        "mysqldump not found in PATH.\nInstallation instructions:\n"
        "  Ubuntu/Debian: sudo apt install default-mysql-client\n"
        "  CentOS/RHEL:   sudo yum install mysql\n"
        "  macOS:         brew install mysql"
    )

    return False


def get_default_backup_filename(db_name: str | None = None):
    """Generate a default backup filename based on the current date and time.

    Params:
        db_name (str): The optional name of the database to include in the filename.

    Returns:
        str: The default backup filename

    """
    timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if db_name:
        return f"{timestamp}_{db_name}_backup.sql"

    return f"{timestamp}_backup.sql"


def save_default_config_json():
    default_app_config = {
        "log_level": "info",
        "db_host": "localhost",
        "db_port": 3306,
        "db_username": "root",
        "db_password": "<mysql-password>",
        "db_database": "db_name",
    }

    with open("mysql_dump_config.json", "w") as f:
        json.dump(default_app_config, f, indent=4)


@dataclass
class DbSettings:
    """Database connection settings.

    Attributes:
        host: MySQL database host
        port: MySQL database port
        username: MySQL database username
        password: MySQL database password
        database: MySQL database name
        backup_file: File to save backup to

    """

    host: str = field(default="localhost")
    port: int = field(default=3306)
    username: str = field(default="root")
    password: str = field(default="", repr=False)
    database: str = field(default="")
    backup_file: str = field(default="backup.sql")


class DatabaseBackupController:
    """Controller class for MySQL database backup operations.

    Attributes:
        args: argparse.Namespace
        logger: logging.Logger
        db_settings: DbSettings
        _connection: pymysql.Connection

    """

    def __init__(
        self,
        args: t.Optional[argparse.Namespace] = None,
        db_settings: t.Optional[t.Union[dict, DbSettings]] = None,
    ):
        self.args = args
        self.logger = logging.getLogger(self.__class__.__name__)

        self.db_settings = self._init_db_settings(db_settings)
        self._validate_settings()

        self._connection = None

    def _init_db_settings(self, settings: dict = None) -> DbSettings:
        """Initialize DbSettings object.

        Params:
            settings (dict): User-provided settings

        Returns:
            DbSettings

        """
        merged = self._merge_settings(self.args, settings or {})

        ## Only keep keys that are fields of DbSettings
        allowed_keys = set(DbSettings.__dataclass_fields__.keys())
        filtered = {k: v for k, v in merged.items() if k in allowed_keys}

        return DbSettings(**filtered)

    def _merge_settings(
        self, args: argparse.Namespace = None, user_settings: dict = None
    ) -> dict:
        """Merge settings from different sources.

        Description:
            Config load priority:
            1. Command-line arguments
            2. User-provided settings
            3. settings.py defaults

        Params:
            args (argparse.Namespace): Command-line arguments
            user_settings (dict): User-provided settings

        Returns:
            dict

        """
        user_settings = user_settings or {}

        ## Start with env defaults
        merged = dict(DB_SETTINGS)
        ## Override with user-provided settings
        merged.update(user_settings)

        ## Helper to safely get from args
        def argval(attr):
            return getattr(args, attr, None) if args else None

        ## Override with CLI args if provided
        cli_mapping = {
            "host": argval("db_host"),
            "port": argval("db_port"),
            "username": argval("db_username"),
            "password": argval("db_password"),
            "database": argval("db_database"),
            "backup_file": argval("backup_file"),
        }

        ## Only override if the CLI value is not None and not empty string
        for k, v in cli_mapping.items():
            if v is not None and v != "":
                merged[k] = v

        ## Set defaults if still missing
        defaults = {
            "host": "localhost",
            "port": 3306,
            "username": "root",
            "password": "",
            "database": "",
            "backup_file": "backup.sql",
        }
        for k, v in defaults.items():
            merged.setdefault(k, v)

        return merged

    def _validate_settings(self) -> None:
        """Validate required database settings."""
        required = ["host", "port", "username", "password", "database"]

        for field in required:
            if not getattr(self.db_settings, field, None):
                raise ValueError(f"Missing required database setting: {field}")

    def _test_connection(self) -> None:
        """Test database connection."""
        self.logger.info(
            f"Connecting to {self.db_settings.database} @ "
            f"{self.db_settings.host}:{self.db_settings.port}"
        )
        try:
            ## Open pymysqlconnection
            self._connection = pymysql.connect(
                host=self.db_settings.host,
                port=self.db_settings.port,
                user=self.db_settings.username,
                password=self.db_settings.password,
                database=self.db_settings.database,
            )
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            raise

    def _build_mysqldump_command(self) -> str:
        """Construct the mysqldump command."""
        return (
            f"mysqldump -h {self.db_settings.host} "
            f"-P {self.db_settings.port} "
            f"-u {self.db_settings.username} "
            f"-p'{self.db_settings.password}' "
            f"{self.db_settings.database} > {self.db_settings.backup_file}"
        )

    def _ensure_backup_dir(self) -> None:
        """Create backup directory if needed."""
        backup_path = Path(self.db_settings.backup_file)

        if not backup_path.parent.exists():
            self.logger.info(f"Creating backup directory: {backup_path.parent}")
            backup_path.parent.mkdir(parents=True, exist_ok=True)

    def run_backup(self) -> None:
        """Execute full backup workflow."""
        ## Check if mysqldump is installed
        if not check_mysqldump_installed():
            raise RuntimeError("mysqldump dependency not met")

        ## Test database connection
        self.logger.info(
            f"Testing connection to {self.db_settings.username}@{self.db_settings.host}:{self.db_settings.port}/{self.db_settings.database}"
        )
        try:
            self._test_connection()
        except Exception as exc:
            self.logger.error(f"Error testing database connection. Details: {exc}")
            raise

        ## Prepare backup environment
        self.logger.info(f"Prepare backup directory & build SQL dump command")
        try:
            self._ensure_backup_dir()
            cmd = self._build_mysqldump_command()
        except Exception as exc:
            self.logger.error(f"Error preparing backup environment: {exc}")
            raise

        ## Do backup
        self.logger.info(f"Starting backup to {self.db_settings.backup_file}")
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Backup failed with exit code {e.returncode}: {e}")
            raise
        except Exception as exc:
            self.logger.error(f"({type(exc)}) Error running mysqldump command: {exc}")
            raise
        finally:
            if self._connection:
                self._connection.close()


def main(
    db_host: str,
    db_port: int,
    db_username: str,
    db_password: str,
    db_database: str,
    backup_file: str,
):
    db_settings: dict = {
        "host": db_host,
        "port": db_port,
        "username": db_username,
        "password": db_password,
        "database": db_database,
        "backup_file": backup_file,
    }

    controller = DatabaseBackupController(db_settings=db_settings)
    try:
        controller.run_backup()
        log.info("Backup completed successfully")
        exit(0)
    except Exception as exc:
        log.error(f"Error dumping MySQL database. Details: {exc}")
        exit(1)


def start_cli():
    """Add arg parsing before main function."""
    args = parse_args()
    ## Set empty user settings dict to populate if --config-file was used
    user_settings = {}

    log_level = "DEBUG" if args.debug else "INFO"
    if (
        "log_level" in user_settings.keys()
        and user_settings.get("log_level") != log_level
    ):
        log_level = user_settings.get(log_level)

    fmt = (
        "%(asctime)s | [%(levelname)s] | %(name)s:%(lineno)s :: %(message)s"
        if args.debug
        else "%(asctime)s [%(levelname)s] :: %(message)s"
    )

    datefmt = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(level=log_level.upper(), format=fmt, datefmt=datefmt)
    log.debug("DEBUG logging enabled")

    ## If --generate-config-file was passed, save the default JSON file
    #  & exit
    if args.generate_config_file:
        save_default_config_json()
        exit(0)

    _config_loaded_from_file = False

    if args.config_file is not None:
        if Path(args.config_file).exists():
            with open(args.config_file, "r") as f:
                user_settings = json.load(f)
                _config_loaded_from_file = True

    ## Define database connection details
    host = (
        user_settings.get("db_host")
        if user_settings.get("db_host")
        else DB_SETTINGS.get("DB_HOST")
    )
    port = (
        user_settings.get("db_port")
        if user_settings.get("db_port")
        else DB_SETTINGS.get("DB_PORT")
    )
    username = (
        user_settings.get("db_username")
        if user_settings.get("db_username")
        else DB_SETTINGS.get("DB_USERNAME")
    )
    password = (
        user_settings.get("db_password")
        if user_settings.get("db_password")
        else DB_SETTINGS.get("DB_PASSWORD")
    )
    database = (
        user_settings.get("db_database")
        if user_settings.get("db_database")
        else DB_SETTINGS.get("DB_DATABASE")
    )

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
    else:
        backup_file = get_default_backup_filename(db_name=database)

    main(
        db_host=host,
        db_port=port,
        db_username=username,
        db_password=password,
        db_database=database,
        backup_file=backup_file,
    )


if __name__ == "__main__":
    try:
        start_cli()
    except Exception as exc:
        log.error(f"Error running MySQL backup script. Details: {exc}")
        exit(1)
