from __future__ import annotations

import db
from depends import db_depends

import sqlalchemy as sa
import sqlalchemy.orm as so

def setup_database(sqla_base: so.DeclarativeBase = db.Base,engine: sa.Engine = db_depends.get_db_engine()) -> None:
    engine: sa.Engine = engine
    db.create_base_metadata(base=sqla_base, engine=engine)
