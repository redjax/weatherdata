import pymysql
import subprocess
import shutil
from dataclasses import dataclass, field
import argparse
from pathlib import Path
import logging
import typing as t

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
    host: str = field(default="localhost")
    port: int = field(default=3306)
    username: str = field(default="root")
    password: str = field(default="", repr=False)
    database: str = field(default="")
    backup_file: str = field(default="backup.sql")


class DatabaseBackupController:
    """Controller class for MySQL database backup operations"""

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
        merged = self._merge_settings(self.args, settings or {})
        ## Only keep keys that are fields of DbSettings
        allowed_keys = set(DbSettings.__dataclass_fields__.keys())
        filtered = {k: v for k, v in merged.items() if k in allowed_keys}
        return DbSettings(**filtered)

    def _merge_settings(
        self, args: argparse.Namespace = None, user_settings: dict = None
    ) -> dict:
        """Merge settings from different sources with priority:
        1. Command-line arguments
        2. User-provided settings
        3. settings.py defaults
        """
        user_settings = user_settings or {}

        # Start with settings.py defaults
        merged = dict(DB_SETTINGS)
        # Update with user-provided settings
        merged.update(user_settings)

        # Helper to safely get from args
        def argval(attr):
            return getattr(args, attr, None) if args else None

        # Override with CLI args if provided
        cli_mapping = {
            "host": argval("db_host"),
            "port": argval("db_port"),
            "username": argval("db_username"),
            "password": argval("db_password"),
            "database": argval("db_database"),
            "backup_file": argval("backup_file"),
        }

        # Only override if the CLI value is not None and not empty string
        for k, v in cli_mapping.items():
            if v is not None and v != "":
                merged[k] = v

        # Set defaults if still missing
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
        """Validate required database settings"""
        required = ["host", "port", "username", "password", "database"]

        for field in required:
            if not getattr(self.db_settings, field, None):
                raise ValueError(f"Missing required database setting: {field}")

    def _check_mysqldump(self) -> bool:
        """Verify mysqldump installation"""
        self.logger.info("Checking mysqldump installation")

        if path := shutil.which("mysqldump"):
            self.logger.debug(f"mysqldump found at: {path}")
            return True

        self.logger.error(
            "mysqldump not found in PATH.\nInstallation instructions:\n"
            "  Ubuntu/Debian: sudo apt install default-mysql-client\n"
            "  CentOS/RHEL:   sudo yum install mysql\n"
            "  macOS:         brew install mysql"
        )
        return False

    def _test_connection(self) -> None:
        """Test database connection"""
        self.logger.info(
            f"Connecting to {self.db_settings.database} @ "
            f"{self.db_settings.host}:{self.db_settings.port}"
        )
        try:
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
        """Construct the mysqldump command"""
        return (
            f"mysqldump -h {self.db_settings.host} "
            f"-P {self.db_settings.port} "
            f"-u {self.db_settings.username} "
            f"-p'{self.db_settings.password}' "
            f"{self.db_settings.database} > {self.db_settings.backup_file}"
        )

    def _ensure_backup_dir(self) -> None:
        """Create backup directory if needed"""
        backup_path = Path(self.db_settings.backup_file)

        if not backup_path.parent.exists():
            self.logger.info(f"Creating backup directory: {backup_path.parent}")
            backup_path.parent.mkdir(parents=True, exist_ok=True)

    def run_backup(self) -> None:
        """Execute full backup workflow"""
        if not self._check_mysqldump():
            raise RuntimeError("mysqldump dependency not met")

        self.logger.info(
            f"Testing connection to {self.db_settings.username}@{self.db_settings.host}:{self.db_settings.port}/{self.db_settings.database}"
        )
        try:
            self._test_connection()
        except Exception as exc:
            self.logger.error(f"Error testing database connection. Details: {exc}")
            raise

        self.logger.info(f"Prepare backup directory & build SQL dump command")
        try:
            self._ensure_backup_dir()
            cmd = self._build_mysqldump_command()
        except Exception as exc:
            self.logger.error(f"Error preparing backup environment: {exc}")
            raise

        self.logger.info(f"Starting backup to {self.db_settings.backup_file}")
        try:
            subprocess.run(cmd, shell=True, check=True)
            self.logger.info("Backup completed successfully")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Backup failed with exit code {e.returncode}: {e}")
            raise
        except Exception as exc:
            self.logger.error(f"({type(exc)}) Error running mysqldump command: {exc}")
            raise
        finally:
            if self._connection:
                self._connection.close()


if __name__ == "__main__":
    args = parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO

    fmt = (
        "%(asctime)s | [%(levelname)s] | %(name)s:%(lineno)s :: %(message)s"
        if args.debug
        else "%(asctime)s [%(levelname)s] :: %(message)s"
    )

    logging.basicConfig(level=log_level, format=fmt, datefmt="%Y-%m-%d %H:%M:%S")

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

    controller = DatabaseBackupController(db_settings=db_settings)
    controller.run_backup()
