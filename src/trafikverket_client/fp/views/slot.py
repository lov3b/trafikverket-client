from __future__ import annotations

import logging
from datetime import date as date_type
from datetime import time as time_type
from typing import TYPE_CHECKING, Iterator

from ..models import (
    ActiveReservationsResponse,
    CreateReservationResponse,
    Occasion,
    OccasionBundle,
    OccasionBundlesData,
)

if TYPE_CHECKING:
    from .._context import HttpContext
    from .reservation import Reservation

logger = logging.getLogger(__name__)


class BookableSlot:
    """A bookable occasion bundle. Call :meth:`reserve` to hold it for 15 minutes."""

    def __init__(
        self,
        context: HttpContext,
        bundle: OccasionBundle,
        licence_id: int,
        examination_type_id: int,
    ) -> None:
        self._context = context
        self._bundle = bundle
        self._licence_id = licence_id
        self._examination_type_id = examination_type_id

    @property
    def data(self) -> OccasionBundle:
        return self._bundle

    @property
    def occasions(self) -> list[Occasion]:
        return self._bundle.occasions

    @property
    def cost(self) -> str:
        return self._bundle.cost

    @property
    def date(self) -> date_type:
        return self._bundle.occasions[0].date

    @property
    def time(self) -> time_type:
        return self._bundle.occasions[0].time

    @property
    def location_name(self) -> str:
        return self._bundle.occasions[0].location_name

    def __repr__(self) -> str:
        return (
            f"BookableSlot({self.date} {self.time} "
            f"at {self.location_name}, {self.cost})"
        )

    async def reserve(self) -> Reservation:
        """Create a 15-minute reservation hold on this slot."""
        from .reservation import Reservation

        body = await self._context.post(
            "create-reservation",
            json={
                "bookingSession": self._context.booking_session(
                    self._licence_id,
                    examination_type_id=self._examination_type_id,
                ),
                "occasionBundle": self._bundle.model_dump(
                    by_alias=True,
                    mode="json",
                ),
            },
        )
        CreateReservationResponse(**body)
        logger.info("Created reservation for licence_id=%d", self._licence_id)

        body = await self._context.post("get-active-reservations")
        active_data = ActiveReservationsResponse(**body).data
        reservations = active_data.active_reservations or []

        # Match by licence + exam type + start time
        occasion_start = self._bundle.occasions[0].duration.start
        for ar in reservations:
            if (
                ar.licence_id == self._licence_id
                and ar.examination_type_id == self._examination_type_id
                and ar.start_date == occasion_start
            ):
                return Reservation(
                    context=self._context,
                    active=ar,
                    licence_id=self._licence_id,
                    examination_type_id=self._examination_type_id,
                )

        # Fallback: if only one reservation, use it
        if len(reservations) == 1:
            return Reservation(
                context=self._context,
                active=reservations[0],
                licence_id=self._licence_id,
                examination_type_id=self._examination_type_id,
            )

        raise RuntimeError(
            "Could not match the created reservation in active reservations"
        )


class SlotList:
    """Iterable list of bookable slots from an occasion-bundles response."""

    def __init__(
        self,
        context: HttpContext,
        data: OccasionBundlesData,
        licence_id: int,
        examination_type_id: int,
    ) -> None:
        self._data = data
        self._slots = [
            BookableSlot(context, bundle, licence_id, examination_type_id)
            for bundle in data.bundles
        ]

    @property
    def data(self) -> OccasionBundlesData:
        return self._data

    @property
    def searched_months(self) -> int:
        return self._data.searched_months

    def __len__(self) -> int:
        return len(self._slots)

    def __iter__(self) -> Iterator[BookableSlot]:
        return iter(self._slots)

    def __getitem__(self, index: int) -> BookableSlot:
        return self._slots[index]

    def __bool__(self) -> bool:
        return bool(self._slots)

    def __repr__(self) -> str:
        return f"SlotList({len(self._slots)} slots)"
