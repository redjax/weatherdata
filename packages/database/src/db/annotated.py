"""Define `Annotated` columns for SQLAlchemy models.

Examples:
    * `INT_PK`: An auto-incrementing, primary key integer value.
    * `STR_10`: A `VARCHAR(10)` column.
    * `STR_255`: A `VARCHAR(255)` column.

"""

from __future__ import annotations

import sqlalchemy as sa
import sqlalchemy.orm as so
from typing_extensions import Annotated
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import JSONB

__all__ = ["INT_PK", "STR_10", "STR_255", "PG_MUT_JSONB"]

## Annotated auto-incrementing integer primary key column
INT_PK = Annotated[
    int, so.mapped_column(sa.INTEGER, primary_key=True, autoincrement=True, unique=True)
]

## SQLAlchemy VARCHAR(10)
STR_10 = Annotated[str, so.mapped_column(sa.VARCHAR(10))]
## SQLAlchemy VARCHAR(255)
STR_255 = Annotated[str, so.mapped_column(sa.VARCHAR(255))]
## Mutable JSONB column (Postgres only)
PG_MUT_JSONB = Annotated[dict, so.mapped_column(MutableDict.as_mutable(JSONB))]
