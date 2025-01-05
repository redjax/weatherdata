from __future__ import annotations

import db
import depends
from loguru import logger as log
import settings
import setup

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    setup.setup_database()
    
    tables = db.show_table_names(engine=depends.get_db_engine())
    
    log.debug(f"Found [{len(tables)}] table(s) in the database.")
    print(f"\nTables [{len(tables)}]:")
    for table in tables:
        print(f"  - {table}")
