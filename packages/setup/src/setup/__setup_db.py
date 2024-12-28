from __future__ import annotations

import db
from depends import db_depends

def setup_database():
    engine = db_depends.get_db_engine()
    db.create_base_metadata(base=db.Base, engine=engine)
