from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from .models import (
    BookingHindrancesData,
    BookingHindrancesResponse,
    Licence,
    LicenceCategory,
    SearchInformationResponse,
    SuggestedReservation,
    SuggestedReservationsResponse,
)

if TYPE_CHECKING:
    from ._context import HttpContext
    from .views import SearchResult

logger = logging.getLogger(__name__)


class BookableLicence:
    """A specific licence within a logged-in session that can be searched and booked."""

    def __init__(
        self,
        context: HttpContext,
        licence_id: int,
        licence: Optional[Licence] = None,
    ) -> None:
        self._context = context
        self._licence_id = licence_id
        self._licence = licence

    @classmethod
    def from_id(cls, context: HttpContext, licence_id: int) -> BookableLicence:
        """Construct from just a licence ID, without fetching details."""
        return cls(context, licence_id, licence=None)

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
                f"BookableLicence(id={self._licence_id}, name={self._licence.name!r}, "
                f"category={self._licence.category.value!r})"
            )
        return f"BookableLicence(id={self._licence_id})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, BookableLicence) and self._licence_id == other._licence_id
        )

    def __hash__(self) -> int:
        return hash(self._licence_id)

    async def search(self, examination_type_id: int = 0) -> SearchResult:
        """Search for bookable occasions under this licence."""
        from .views import SearchResult

        body = await self._context.post(
            "search-information",
            json={
                "bookingSession": self._context.booking_session(
                    self._licence_id,
                    examination_type_id=examination_type_id,
                ),
            },
        )
        parsed = SearchInformationResponse(**body)
        logger.debug(
            "Fetched search information for licence_id=%d, %d locations",
            self._licence_id,
            len(parsed.data.locations),
        )
        return SearchResult(
            context=self._context,
            data=parsed.data,
            licence_id=self._licence_id,
            examination_type_id=examination_type_id,
        )

    async def get_booking_hindrances(
        self,
        booking_mode_id: int = 0,
        examination_type_id: int = 0,
    ) -> BookingHindrancesData:
        body = await self._context.post(
            "booking-hindrances",
            json={
                "bookingSession": self._context.booking_session(
                    self._licence_id,
                    booking_mode_id=booking_mode_id,
                    examination_type_id=examination_type_id,
                ),
            },
        )
        parsed = BookingHindrancesResponse(**body)
        logger.debug(
            "Booking hindrances for licence_id=%d: can_book=%s",
            self._licence_id,
            parsed.data.can_book_licence,
        )
        return parsed.data

    async def get_suggested_reservations(self) -> list[SuggestedReservation] | None:
        body = await self._context.post(
            "get-suggested-reservations-by-licence-and-ssn",
            json={
                "licenceId": self._licence_id,
                "ssn": self._context.personal_identity_number,
            },
        )
        parsed = SuggestedReservationsResponse(**body)
        logger.debug(
            "Fetched suggested reservations for licence_id=%d", self._licence_id
        )
        return parsed.data
