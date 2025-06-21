from __future__ import annotations

import argparse
import json
from pathlib import Path
import datetime as dt

import duckdb
from loguru import logger as log
import pandas as pd
import settings
import setup
import sqlalchemy as sa
import sqlalchemy.orm as so

LOGGING_SETTINGS = settings.get_namespace("logging")


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--jobs-file", type=str, help="Path to a JSON file with jobs & connections"
    )

    args = parser.parse_args()

    return args


def get_ts(fmt: str = "full") -> str:
    match fmt:
        case "full":
            ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        case "date":
            ts = dt.datetime.now().strftime("%Y%m%d")
        case "time":
            ts = dt.datetime.now().strftime("%H-%M-%S")
    
    return ts


def load_jobs(jobs_file: str):
    if not jobs_file:
        raise ValueError("Missing path to a job file")
    if not Path(str(jobs_file)).exists():
        raise FileNotFoundError(f"Could not find jobs file at path '{jobs_file}'.")

    log.debug(f"Loading jobs configuration from: {jobs_file}")
    try:
        with open(jobs_file, "r") as f:
            config = json.load(f)

            return config
    except Exception as exc:
        log.error(f"Failed reading jobs from file '{jobs_file}'. Details: {exc}")
        raise exc


def get_password(password_file: str) -> str:
    if not password_file:
        return ""
    if not Path(str(password_file)).exists():
        raise FileNotFoundError(
            f"Could not find password file at path: {password_file}"
        )

    log.debug(f"Loading password from file: {password_file}")
    try:
        with open(password_file, "r") as f:
            return f.read().strip()
    except Exception as exc:
        log.error(
            f"Failed loading database password from file '{password_file}'. Details: {exc}"
        )
        raise exc


def build_connection_string(conn_cfg: dict, password: str):
    match conn_cfg["type"]:
        case "sqlite":
            return f"sqlite:///{conn_cfg['database']}"
        case "postgres:":
            return (
                f"postgresql+psycopg2://{conn_cfg['username']}:{password}"
                f"@{conn_cfg['host']}:{conn_cfg['port']}/{conn_cfg['database']}"
            )
        case "mysql":
            return (
                f"mysql+pymysql://{conn_cfg['username']}:{password}"
                f"@{conn_cfg['host']}:{conn_cfg['port']}/{conn_cfg['database']}"
            )
        case _:
            raise ValueError(f"Unsupported database type: {conn_cfg['type']}")


def get_connection_config(connections: list[dict], name: str):
    """Extract conection details from a JSON config object."""
    for conn in connections:
        if conn["name"] == name:
            return conn

    raise ValueError(f"No connection found with name '{name}'")


def export_tables_to_json(conn_cfg: dict, tables: list[str], output_path: str, output_format: str):
    log.debug(f"Connection config: {conn_cfg}")

    password: str = get_password(conn_cfg.get("password_file", ""))
    conn_str: str = build_connection_string(conn_cfg, password)
    
    engine: sa.Engine = sa.create_engine(conn_str)
    
    log.debug(f"Creating in-memory DuckDB database for exported data")
    ## in-memory duckdb connection
    con = duckdb.connect()
    
    _split_output_dir = Path(str(output_path)).parent / get_ts(fmt="date")
    _split_output_filename = Path(str(output_path)).name
    # log.debug(f"Output dir: {_split_output_dir}")
    # log.debug(f"Output filename: {_split_output_filename}")
    
    ## Join parts back together with new date directory
    output_path = str(_split_output_dir / _split_output_filename)
    log.debug(f"Output path: {output_path}")

    if not Path(str(output_path)).parent.exists():
        try:
            Path(str(output_path)).parent.mkdir(exist_ok=True, parents=True)
        except Exception as exc:
            log.error(f"Failed creating output directory. Details: {exc}")
            raise

    for table in tables:
        ## New in-memory DB for each table
        con = duckdb.connect()

        ## Create output file name
        this_output = output_path.format(ts=get_ts(fmt="time"), table=table)
        log.debug(f"This output: {this_output}")

        if not Path(this_output).parent.exists():
            Path(this_output).parent.mkdir(exist_ok=True, parents=True)

        log.info(f"Exporting table '{table}' from {conn_cfg['name']} to {this_output} (format: {output_format})")
        try:
            df: pd.DataFrame = pd.read_sql_table(table, engine)
            con.register(table, df)

            match output_format:
                case "json":
                    con.execute(
                        f"COPY (SELECT * FROM {table}) TO '{this_output}' (FORMAT JSON, ARRAY)"
                    )
                    log.info(f"Exported {len(df)} rows to {this_output}")
                    
                case "parquet":
                    con.execute(
                        f"COPY (SELECT * FROM {table}) TO '{this_output}' (FORMAT PARQUET)"
                    )
                case _:
                    raise ValueError(f"Unknown export format: {output_format}")

        except Exception as exc:
            log.error(f"Failed exporting table '{table}'. Details: {exc}")
            raise

    log.info(f"Data exported to path: {Path(output_path).parent}")


def import_tables(
    conn_cfg: dict,
    tables: list[str],
    input_path_template: str,
    dump_format: str = "json",
    deduplicate_on: list[str] = None,
    ts: str = None
):
    """Import tables from files (JSON or Parquet) into the target DB."""
    log.debug(f"Connection config: {conn_cfg}")

    password = get_password(conn_cfg.get("password_file", ""))
    conn_str = build_connection_string(conn_cfg, password)
    engine = sa.create_engine(conn_str)

    ## If no timestamp is provided, try today's date or glob for latest
    if ts is None:
        ## or "full" if you want to match full timestamps
        ts = get_ts(fmt="date")

    for table in tables:
        ## Build input path
        input_path = input_path_template.replace("{table}", table).replace("{ts}", ts)
        input_path_obj = Path(input_path)

        ## If file doesn't exist, try to glob for the latest matching file
        if not input_path_obj.exists():
            files = sorted(input_path_obj.parent.glob(f"*_{table}.{dump_format}"), reverse=True)
            if not files:
                log.error(f"No input file found for table '{table}' at {input_path}")
                continue
            input_path = str(files[0])
            log.info(f"Using latest file for table '{table}': {input_path}")

        con = duckdb.connect()
        log.info(f"Importing table '{table}' from {input_path} into {conn_cfg['name']} (format: {dump_format})")
        
        try:
            match dump_format:
                case "json":
                    df = con.execute(f"SELECT * FROM read_json_auto('{input_path}')").df()
                case "parquet":
                    df = con.execute(f"SELECT * FROM read_parquet('{input_path}')").df()
                case _:
                    raise ValueError(f"Unsupported dump_format: {dump_format}")
            
            if deduplicate_on:
                df = df.drop_duplicates(subset=deduplicate_on)

            df.to_sql(table, engine, if_exists="append", index=False)
            log.info(f"Imported {len(df)} rows into {table}")

        except Exception as exc:
            log.error(f"Failed importing table '{table}'. Details: {exc}")
            raise


def run(connections: list[dict], jobs: list[dict]):
    if not connections:
        raise ValueError("Missing list of connections")
    if not isinstance(connections, list):
        raise TypeError("Invalid type for 'connection': {type(connections)}. Must be a list of connection dicts")
    if not len(connections) > 0:
        raise ValueError("Must pass a list with at least 1 connection object")

    log.debug(f"Connections: {len(connections)}, Jobs: {len(jobs)}")

    for job in jobs:
        log.debug(f"Executing job: {job}")

        match job["type"]:
            case "export":
                conn_cfg = get_connection_config(connections, job["connection"])
                try:
                    export_tables_to_json(conn_cfg, job["tables"], job["dump_path"], output_format=job["dump_format"])
                except Exception as exc:
                    log.error(f"Failed job: {job}. Details: {exc}")
                    continue

            case "import":
                conn_cfg = get_connection_config(connections, job["connection"])
                import_tables(
                    conn_cfg,
                    job["tables"],
                    job["dump_path"],
                    dump_format=job.get("dump_format", "json"),
                    deduplicate_on=job.get("deduplicate_on"),
                    ## Optionally pass a specific timestamp if you want
                    ts=None,
                )
            case _:
                raise ValueError(f"Unknown job type: {job['type']}")


def main():
    args = parse_arguments()

    log_level = (
        "DEBUG" if args.debug else LOGGING_SETTINGS.get("LOG_LEVEL", "INFO").upper()
    )
    setup.setup_loguru_logging(log_level=log_level.upper())

    log.debug("DEBUG logging enabled")

    if not args.jobs_file or args.jobs_file == "":
        raise ValueError(
            "Missing path to a JSON file with jobs & connections for the data mover."
        )

    try:
        config = load_jobs(args.jobs_file)
    except Exception as exc:
        raise
    # log.debug(f"Jobs configuration: {config}")

    connections = config["connections"]
    log.debug(f"Job connecetions: {connections}")
    jobs = config["jobs"]
    log.debug(f"Jobs: {jobs}")

    try:
        run(connections, jobs)
    except Exception as exc:
        raise exc


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log.error(exc)
