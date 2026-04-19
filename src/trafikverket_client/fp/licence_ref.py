from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Optional

from .models import (
    BookingHindrancesData,
    Licence,
    LicenceCategory,
    OccasionBundle,
    OccasionBundlesData,
    ReservationInformationData,
    SearchInformationData,
    SuggestedReservation,
)

if TYPE_CHECKING:
    from .logged_in_client import LoggedinClient


class LicenceRef:
    """A handle to a specific licence on a specific logged-in session."""

    def __init__(
        self,
        client: "LoggedinClient",
        licence_id: int,
        licence: Optional[Licence] = None,
    ) -> None:
        self._client = client
        self._licence_id = licence_id
        self._licence = licence

    @classmethod
    def raw(cls, client: "LoggedinClient", licence_id: int) -> "LicenceRef":
        """Construct a handle without a server round-trip."""
        return cls(client, licence_id, licence=None)

    @property
    def id(self) -> int:
        return self._licence_id

    @property
    def licence(self) -> Optional[Licence]:
        return self._licence

    @property
    def name(self) -> Optional[str]:
        return self._licence.name if self._licence else None

    @property
    def category(self) -> Optional[LicenceCategory]:
        return self._licence.category if self._licence else None

    def __repr__(self) -> str:
        if self._licence:
            return (
                f"LicenceRef(id={self._licence_id}, name={self._licence.name!r}, "
                f"category={self._licence.category.value!r})"
            )
        return f"LicenceRef(id={self._licence_id}, raw=True)"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, LicenceRef) and self._licence_id == other._licence_id

    def __hash__(self) -> int:
        return hash(self._licence_id)

    async def booking_hindrances(
        self,
        booking_mode_id: int = 0,
        examination_type_id: int = 0,
    ) -> BookingHindrancesData:
        return await self._client.booking_hindrances(
            licence_id=self._licence_id,
            booking_mode_id=booking_mode_id,
            examination_type_id=examination_type_id,
        )

    async def get_confirmed_examinations(self) -> list[dict]:
        return await self._client.get_confirmed_examinations(
            licence_id=self._licence_id
        )

    async def get_suggested_reservations(self) -> list[SuggestedReservation] | None:
        return await self._client.get_suggested_reservations(
            licence_id=self._licence_id
        )

    async def search_information(
        self,
        examination_type_id: int = 0,
        booking_mode_id: int = 0,
    ) -> SearchInformationData:
        return await self._client.search_information(
            licence_id=self._licence_id,
            examination_type_id=examination_type_id,
            booking_mode_id=booking_mode_id,
        )

    async def occasion_bundles(
        self,
        examination_type_id: int,
        location_id: int,
        start_date: datetime | None = None,
        **kwargs: Any,
    ) -> OccasionBundlesData:
        if start_date is None:
            start_date = datetime.now(timezone.utc)
        return await self._client.occasion_bundles(
            licence_id=self._licence_id,
            examination_type_id=examination_type_id,
            location_id=location_id,
            start_date=start_date,
            **kwargs,
        )

    async def create_reservation(
        self,
        examination_type_id: int,
        occasion_bundle: OccasionBundle,
        booking_mode_id: int = 0,
    ) -> None:
        return await self._client.create_reservation(
            licence_id=self._licence_id,
            examination_type_id=examination_type_id,
            occasion_bundle=occasion_bundle,
            booking_mode_id=booking_mode_id,
        )

    async def reservation_information(
        self,
        examination_type_id: int,
        booking_mode_id: int = 0,
    ) -> ReservationInformationData:
        return await self._client.reservation_information(
            licence_id=self._licence_id,
            examination_type_id=examination_type_id,
            booking_mode_id=booking_mode_id,
        )
