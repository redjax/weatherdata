from __future__ import annotations

import argparse

import db
import depends
from loguru import logger as log
import settings
import setup

def parse_args():
    parser = argparse.ArgumentParser(
        description="Count number of rows in a given database table."
    )
    parser.add_argument(
        "-n", "--table-name",
        type=str,
        # required=True,
        help="Name of the database table to count rows in."
    )
    parser.add_argument(
        "--show-tables",
        action="store_true",
        help="List all table names in the database."
    )

    return parser.parse_args()


if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    setup.setup_database()
    
    args = parse_args()
    
    if args.show_tables:
        tables = db.show_table_names(engine=depends.get_db_engine())
        
        log.debug(f"Found [{len(tables)}] table(s) in the database.")

        print(f"\nTables [{len(tables)}]:")
        for table in tables:
            print(f"  - {table}")

        exit(0)
    
    if not args.table_name:
        print(f"[WARNING] Missing a --table-name (-n). Please re-run with -n 'table_name'.")
        exit(1)

    try:
        db.count_table_rows(table=args.table_name, engine=depends.get_db_engine())
    except Exception as exc:
        msg = f"({type(exc)}) Error counting rows in table '{args.table_name}'. Details: {exc}"
        log.error(msg)
        
        raise exc
