from __future__ import annotations

from contextlib import contextmanager
import importlib.util
import logging
import os
from pathlib import Path
import platform
import shutil
import typing as t

import nox

## Set nox options
if importlib.util.find_spec("uv"):
    nox.options.default_venv_backend = "uv|virtualenv"
else:
    nox.options.default_venv_backend = "virtualenv"
nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = False
nox.options.error_on_missing_interpreters = False
# nox.options.report = True

## Define sessions to run when no session is specified
nox.sessions = ["ruff-lint", "export"]

## Create logger for this module
log: logging.Logger = logging.getLogger("nox")

## Define versions to test
PY_VERSIONS: list[str] = ["3.12", "3.11"]
## Get tuple of Python ver ('maj', 'min', 'mic')
PY_VER_TUPLE: tuple[str, str, str] = platform.python_version_tuple()
## Dynamically set Python version
DEFAULT_PYTHON: str = f"{PY_VER_TUPLE[0]}.{PY_VER_TUPLE[1]}"

## Set directory for requirements.txt file output
REQUIREMENTS_OUTPUT_DIR: Path = Path(".")

# this VENV_DIR constant specifies the name of the dir that the `dev`
# session will create, containing the virtualenv;
# the `resolve()` makes it portable
VENV_DIR = Path("./.venv").resolve()

LINT_PATHS: list[str] = ["src", "packages", "applications", "sandbox"]


def install_uv_project(session: nox.Session, external: bool = False) -> None:
    """Method to install uv and the current project in a nox session."""
    log.info("Installing uv in session")
    session.install("uv")
    log.info("Syncing uv project")
    session.run("uv", "sync", external=external)
    log.info("Installing project")
    session.run("uv", "pip", "install", ".", external=external)


@contextmanager
def cd(new_dir) -> t.Generator[None, t.Any, None]:  # type: ignore
    """Context manager to change a directory before executing command."""
    prev_dir: str = os.getcwd()
    os.chdir(os.path.expanduser(new_dir))
    try:
        yield
    finally:
        os.chdir(prev_dir)


@nox.session(name="dev-env", tags=["setup"])
def dev(session: nox.Session) -> None:
    """Sets up a python development environment for the project.

    Run this on a fresh clone of the repository to automate building the project with uv.
    """
    install_uv_project(session, external=True)


@nox.session(python=[DEFAULT_PYTHON], name="ruff-lint", tags=["ruff", "clean", "lint"])
def run_linter(session: nox.Session, lint_paths: list[str] = LINT_PATHS):
    """Nox session to run Ruff code linting."""
    if not Path("ruff.toml").exists():
        if not Path("pyproject.toml").exists():
            log.warning(
                """No ruff.toml file found. Make sure your pyproject.toml has a [tool.ruff] section!

If your pyproject.toml does not have a [tool.ruff] section, ruff's defaults will be used.
Double check imports in _init_.py files, ruff removes unused imports by default.
"""
            )

    session.install("ruff")

    log.info("Linting code")
    for d in lint_paths:
        if not Path(d).exists():
            log.warning(f"Skipping lint path '{d}', could not find path")
            pass
        else:
            lint_path: Path = Path(d)
            log.info(f"Running ruff imports sort on '{d}'")
            session.run(
                "ruff",
                "check",
                lint_path,
                "--select",
                "I",
                "--fix",
            )

            log.info(f"Running ruff checks on '{d}' with --fix")
            session.run(
                "ruff",
                "check",
                lint_path,
                "--fix",
            )

    # log.info("Linting noxfile.py")
    # session.run(
    #     "ruff",
    #     "check",
    #     f"{Path('./noxfile.py')}",
    #     "--fix",
    # )

    ## Find stray Python files not in src/, .venv/, or .nox/
    all_python_files = [
        f
        for f in Path("./").rglob("*.py")
        if ".venv" not in f.parts
        and "migrations" not in f.parts
        and ".nox" not in f.parts
        and "src" not in f.parts
    ]
    log.info(f"Found [{len(all_python_files)}] Python file(s) to lint")
    for py_file in all_python_files:
        log.info(f"Linting Python file: {py_file}")
        session.run("ruff", "check", str(py_file), "--fix")


@nox.session(python=[DEFAULT_PYTHON], name="vulture-check", tags=["quality"])
def run_vulture_check(session: nox.Session):
    session.install(f"vulture")

    log.info("Checking for dead code with vulture")
    session.run("vulture", "src/", "--min-confidence", "100")
    session.run("vulture", "packages/", "--min-confidence", "100")
    session.run("vulture", "applications/", "--min-confidence", "100")


@nox.session(python=[DEFAULT_PYTHON], name="uv-export")
@nox.parametrize("requirements_output_dir", REQUIREMENTS_OUTPUT_DIR)
def export_requirements(session: nox.Session, requirements_output_dir: Path):
    ## Ensure REQUIREMENTS_OUTPUT_DIR path exists
    if not requirements_output_dir.exists():
        try:
            requirements_output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            msg = Exception(
                f"Unable to create requirements export directory: '{requirements_output_dir}'. Details: {exc}"
            )
            log.error(msg)

            requirements_output_dir: Path = Path("./")

    session.install(f"uv")

    log.info("Exporting production requirements")
    session.run(
        "uv",
        "pip",
        "compile",
        "pyproject.toml",
        "-o",
        str(REQUIREMENTS_OUTPUT_DIR / "requirements.txt"),
    )


## Run pytest with xdist, allowing concurrent tests
@nox.session(python=DEFAULT_PYTHON, name="tests")
def run_tests(session: nox.Session):
    install_uv_project(session)
    session.install("pytest-xdist")

    print("Running Pytest tests")
    session.run(
        "uv",
        "run",
        "pytest",
        "-n",
        "auto",
        "--tb=auto",
        "-v",
        "-rsXxfP",
    )


@nox.session(name="init-clone-setup")
def run_init_clone_setup(session: nox.Session):
    install_uv_project(session)

    copy_paths = [
        {"src": "./config/settings.toml", "dest": "./config/settings.local.toml"},
        {"src": "./config/.secrets.toml", "dest": "./config/.secrets.local.toml"},
        # {
        #     "src": "./config/celery/settings.toml",
        #     "dest": "./config/celery/settings.local.toml"
        # },
        # {
        #     "src": "./config/celery/.secrets.toml",
        #     "dest": "./config/celery/.secrets.local.toml"
        # },
        # {
        #     "src": "./config/database/settings.toml",
        #     "dest": "./config/database/settings.local.toml"
        # },
        # {
        #     "src": "./config/database/.secrets.toml",
        #     "dest": "./config/database/.secrets.local.toml"
        # },
        # {
        #     "src": "./config/dramatiq/settings.toml",
        #     "dest": "./config/dramatiq/settings.local.toml"
        # },
        # {
        #     "src": "./config/dramatiq/.secrets.toml",
        #     "dest": "./config/dramatiq/.secrets.local.toml"
        # },
        # {
        #     "src": "./config/fastapi/settings.toml",
        #     "dest": "./config/fastapi/settings.local.toml"
        # },
        # {
        #     "src": "./config/fastapi/.secrets.toml",
        #     "dest": "./config/fastapi/.secrets.local.toml"
        # },
        # {
        #     "src": "./config/uvicorn/settings.toml",
        #     "dest": "./config/uvicorn/settings.local.toml"
        # },
        # {
        #     "src": "./config/uvicorn/.secrets.toml",
        #     "dest": "./config/uvicorn/.secrets.local.toml"
        # },
        # {
        #     "src": "./config/weatherapi/settings.toml",
        #     "dest": "./config/weatherapi/settings.local.toml"
        # },
        # {
        #     "src": "./config/weatherapi/.secrets.toml",
        #     "dest": "./config/weatherapi/.secrets.local.toml"
        # },
        {"src": "./containers/.env.example", "dest": "./containers/.env"},
        {
            "src": "./containers/envs/dev.app.env.example",
            "dest": "./containers/envs/dev.app.env",
        },
        {
            "src": "./containers/envs/dev.messaging.env.example",
            "dest": "./containers/envs/dev.messaging.env",
        },
    ]

    for p in copy_paths:
        if not Path(p["dest"]).exists():
            log.info(f"Copying {p['src']} to {p['dest']}")
            shutil.copyfile(p["src"], p["dest"])

        else:
            log.info(f"{p['dest']} already exists, skipping copy")


###########
# Alembic #
###########


@nox.session(python=[DEFAULT_PYTHON], name="alembic-migrate", tags=["alembic", "db"])
def run_alembic_migrations(session: nox.Session):
    # session.install("alembic")
    install_uv_project(session)

    log.info("Running database migrations with alembic")

    session.run(
        "alembic", "revision", "--autogenerate", "-m", "'autogenerated migration'"
    )
    session.run("alembic", "upgrade", "head")


@nox.session(python=[DEFAULT_PYTHON], name="alembic-upgrade", tags=["alembic", "db"])
def run_alembic_migrations(session: nox.Session):
    # session.install("alembic")
    install_uv_project(session)

    revision = input("Revision to upgrade (default: 'head'): ") or "head"
    log.info(f"Running alembic upgrade {revision}")

    session.run("alembic", "upgrade", revision)


@nox.session(python=[DEFAULT_PYTHON], name="alembic-init", tags=["init"])
def run_alembic_initialization(session: nox.Session):
    if Path("./alembic").exists():
        log.warning("Migrations directory [./alembic] exists. Skipping alembic init.")
        return

    install_uv_project(session)

    log.info("Initializing Alembic database")

    session.run("alembic", "init", "migrations")

    log.info(
        """
!! READ THIS !!

Alembic initialized at path ./migrations.

You must edit migrations/env.py to configure your project.

If you're using a "src" layout, add this to the top of your code:

import sys

sys.path.append("./src")

Import your SQLAlchemy models (look for the commented sections describing model imports),
set your SQLAlchemy Base.metadata, and set the database URI.

If you're using Dynaconf, i.e. in a `db.settings.DB_SETTINGS` object, you can set the
database URI like:

## Get database URI from config
#  !! You have to write this function !!
DB_URI = get_db_uri()
## Set alembic's SQLAlchemy URL
if DB_URI:
    config.set_main_option(
        "sqlalchemy.url", DB_URI.render_as_string(hide_password=False)
    )
else:
    raise Exception("DATABASE_URL not found in Dynaconf settings")
    
!! READ THIS !! 
"""
    )
