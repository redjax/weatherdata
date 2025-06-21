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
## Define tables & columns with unique constraints to deduplicate on
DEDUP_KEYS = {
    "weatherapi_location": ["name", "country"],
    "weatherapi_current_weather": ["last_updated_epoch"],
    "weatherapi_current_condition": ["weather_id"],
    "weatherapi_air_quality": ["weather_id"],
}


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
        case "postgres":
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


def export_tables(conn_cfg: dict, tables: list[str], output_path: str, output_format: str):
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
    conn_cfg,
    tables,
    input_path_template,
    dump_format="json",
    ts=None
):
    password = get_password(conn_cfg.get("password_file", ""))
    conn_str = build_connection_string(conn_cfg, password)
    engine = sa.create_engine(conn_str)

    if ts is None:
        ts = get_ts(fmt="date")

    id_maps = {}

    for table in tables:
        input_path = input_path_template.replace("{table}", table).replace("{ts}", ts)
        input_path_obj = Path(input_path)

        if not input_path_obj.exists():
            ext = dump_format if dump_format in ("json", "parquet") else "*"
            files = sorted(
                input_path_obj.parent.glob(f"*_{table}.{ext}"),
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )
            if not files:
                log.error(f"No input file found for table '{table}' at {input_path}")
                continue
            input_path = str(files[0])
            log.info(f"Using latest file for table '{table}': {input_path}")

        con = duckdb.connect()

        log.info(f"Importing table '{table}' from {input_path} into {conn_cfg['name']} (format: {dump_format})")
        try:
            # Load file using DuckDB
            if dump_format == "json":
                df = con.execute(f"SELECT * FROM read_json_auto('{input_path}')").df()
            elif dump_format == "parquet":
                df = con.execute(f"SELECT * FROM read_parquet('{input_path}')").df()
            else:
                raise ValueError(f"Unsupported dump_format: {dump_format}")

            has_id_column = "id" in df.columns
            if has_id_column:
                log.debug("Removing 'id' column from import data")
                df["__source_id__"] = df["id"]
                df.drop(columns=["id"], inplace=True)

            if df.empty:
                log.info(f"No rows to import for {table}.")
                continue

            before = len(df)

            # Deduplication logic
            log.debug("Fetching existing rows for duplicate check")
            try:
                existing = pd.read_sql_table(table, engine)
                if "id" in existing.columns:
                    existing.drop(columns=["id"], inplace=True)
            except Exception as exc:
                log.warning(f"Failed fetching existing rows from {table}: {exc}")
                existing = pd.DataFrame(columns=df.columns)

            dedup_columns = DEDUP_KEYS.get(table)
            if dedup_columns:
                log.debug(f"Using DEDUP_KEYS for {table}: {dedup_columns}")
                try:
                    existing_subset = existing[dedup_columns].drop_duplicates()
                    df_subset = df[dedup_columns].drop_duplicates()

                    merged = df_subset.merge(existing_subset, how="left", indicator=True)
                    new_keys = merged[merged["_merge"] == "left_only"].drop(columns=["_merge"])

                    df = df.merge(new_keys, on=dedup_columns, how="inner")
                except Exception as exc:
                    log.error(f"Deduplication failed for table '{table}'. Details: {exc}")
                    raise
            else:
                log.debug(f"No DEDUP_KEYS defined for {table}. Falling back to full-row deduplication.")
                merged = df.merge(existing.drop_duplicates(), how="left", indicator=True)
                df = merged[merged["_merge"] == "left_only"].drop(columns=["_merge"])

            skipped = before - len(df)
            if skipped > 0:
                log.info(f"Skipped {skipped} duplicate rows for {table} (already present).")

            if df.empty:
                log.info(f"No new rows to import for {table}.")
                continue

            # Update foreign keys using id_maps and filter missing
            for col in df.columns:
                if col.endswith("_id"):
                    ref_table = col[:-3]
                    if ref_table in id_maps:
                        if col in df.columns:
                            df[col] = df[col].map(id_maps[ref_table]).fillna(df[col])
                    else:
                        # Fetch valid foreign keys from parent table
                        try:
                            valid_ids = pd.read_sql_table(ref_table, engine)["id"].tolist()
                            before_filter = len(df)
                            df = df[df[col].isin(valid_ids)]
                            after_filter = len(df)
                            if after_filter < before_filter:
                                log.info(f"Filtered {before_filter - after_filter} rows from '{table}' due to missing foreign keys in '{ref_table}'")
                        except Exception as exc:
                            log.warning(f"Could not validate foreign key {col} in {table}: {exc}")

            # Capture __source_id__ before dropping it
            has_source_id = "__source_id__" in df.columns
            df_source_map = df[["__source_id__"] + dedup_columns].copy() if has_source_id and dedup_columns else None

            # Drop __source_id__ before database insert
            if has_source_id:
                df.drop(columns=["__source_id__"], inplace=True)

            # Insert into database
            df.to_sql(table, engine, if_exists="append", index=False)
            log.info(f"Imported {len(df)} rows into {table}")

            # Build id_map for this table if needed
            if has_id_column and df_source_map is not None:
                try:
                    db_rows = pd.read_sql_table(table, engine)
                    db_rows = db_rows[dedup_columns + ["id"]].drop_duplicates()
                    merged = df_source_map.merge(db_rows, on=dedup_columns, how="inner")
                    id_maps[table] = dict(zip(merged["__source_id__"], merged["id"]))
                    log.debug(f"Built id_map for {table} with {len(id_maps[table])} entries.")
                except Exception as exc:
                    log.warning(f"Could not build id_map for {table}: {exc}")

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
                    export_tables(conn_cfg, job["tables"], job["dump_path"], output_format=job["dump_format"])
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
                    # deduplicate_on=job.get("deduplicate_on"),
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
