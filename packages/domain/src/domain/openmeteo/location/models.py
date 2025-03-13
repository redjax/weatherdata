from decimal import Decimal

import typing as t

from db import Base, annotated, StrList

from loguru import logger as log
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so

__all__ = ["MeteoLocationModel"]


class MeteoLocationModel(Base):
    __tablename__ = "openmeteo_location"
    __table_args__ = (sa.UniqueConstraint("id", name="_id_uc"),)

    location_id: so.Mapped[annotated.INT_PK]

    id: so.Mapped[int] = so.mapped_column(
        sa.NUMERIC, nullable=False, unique=True, index=True
    )
    name: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    latitude: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    longitude: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    elevation: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    feature_code: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    country_code: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    admin1_id: so.Mapped[int] = so.mapped_column(sa.NUMERIC, nullable=False)
    admin2_id: so.Mapped[int] = so.mapped_column(sa.NUMERIC, nullable=False)
    admin3_id: so.Mapped[int] = so.mapped_column(sa.NUMERIC, nullable=False)
    timezone: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    population: so.Mapped[int] = so.mapped_column(sa.NUMERIC, nullable=False)
    postcodes: so.Mapped[list[str]] = so.mapped_column(
        sa.JSON()
        .with_variant(JSONB, "postgresql")
        .with_variant(sa.JSON, "mysql")
        .with_variant(sa.TEXT, "sqlite"),
        nullable=False,
    )
    country_id: so.Mapped[int] = so.mapped_column(sa.NUMERIC, nullable=False)
    country: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    admin1: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    admin2: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
    admin3: so.Mapped[str] = so.mapped_column(sa.TEXT, nullable=False)
