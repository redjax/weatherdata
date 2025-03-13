import typing as t
from decimal import Decimal

from .models import MeteoLocationModel

from db.base import BaseRepository
from loguru import logger as log
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so

__all__ = ["LocationRepository"]


class LocationRepository(BaseRepository[MeteoLocationModel]):
    """Repository for LocationModel objects.

    Attributes:
        session (so.Session): The database session.

    """

    def __init__(self, session: so.Session):
        super().__init__(session, MeteoLocationModel)

    def get_by_id(self, id: int) -> MeteoLocationModel | None:
        """Get a location by its ID.

        Params:
            id (int): The ID of the location to retrieve.

        Returns:
            (LocationModel): A LocationModel object.
            (None): None if no location is found matching criteria.

        """
        return (
            self.session.query(MeteoLocationModel)
            .filter(MeteoLocationModel.location_id == id)
            .one_or_none()
        )

    def get_by_openmeteo_id(self, id: int) -> MeteoLocationModel | None:
        """Get a location by its ID.

        Params:
            id (int): The ID of the location to retrieve.

        Returns:
            (LocationModel): A LocationModel object.
            (None): None if no location is found matching criteria.

        """
        return (
            self.session.query(MeteoLocationModel)
            .filter(MeteoLocationModel.id == id)
            .one_or_none()
        )

    def get_by_country(self, country: str) -> list[MeteoLocationModel] | None:
        """Get a location by its country.

        Params:
            country (str): The country of the location.

        Returns:
            (MeteoLocationModel): A MeteoLocationModel object.
            (None): None if no location is found matching criteria.

        """
        return (
            self.session.query(MeteoLocationModel)
            .filter(MeteoLocationModel.country == country)
            .all()
        )

    def get_by_lat_lon(
        self, lat_lon: tuple[Decimal, Decimal]
    ) -> MeteoLocationModel | None:
        """Get a location by its latitude and longitude.

        Params:
            lat_lon (tuple[Decimal, Decimal]): The latitude and longitude of the location.

        Returns:
            (MeteoLocationModel): A MeteoLocationModel object.
            (None): None if no location is found matching criteria.

        """
        return (
            self.session.query(MeteoLocationModel)
            .filter(
                MeteoLocationModel.latitude == lat_lon[0]
                and MeteoLocationModel.longitude == lat_lon[1]
            )
            .one_or_none()
        )

    def save(self, location: MeteoLocationModel) -> MeteoLocationModel | None:
        """Save a location to the database.

        Params:
            location (MeteoLocationModel): The location to save.

        Returns:
            MeteoLocationModel: The saved location.

        Raises:
            Exception: If location cannot be saved, an `Exception` is raised.

        """
        ## Check if location already exists
        existing_location: MeteoLocationModel | None = self.get_by_id(location.id)

        if existing_location:
            log.info(
                f"Location already exists: {location.name}, {location.admin1} {location.country}. Returning from database."
            )
            return self.get_by_id(location.id)

        try:
            self.session.add(location)
            self.session.commit()
            self.session.refresh(location)

            return location
        except sa_exc.IntegrityError as exc:
            msg = f"({type(exc)}) Error saving location. Details: {exc}"
            log.error(msg)
            raise
