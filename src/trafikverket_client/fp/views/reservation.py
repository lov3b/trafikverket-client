from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from .._temporal import serialize_second_datetime
from ..models import (
    ActiveReservation,
    Examination,
    InvoicePaymentResponse,
    ReservationInformationData,
    ReservationInformationResponse,
    ReservationTimeResponse,
    SummaryData,
    SummaryResponse,
)

if TYPE_CHECKING:
    from .._context import HttpContext

logger = logging.getLogger(__name__)


class Reservation:
    """A 15-minute hold on a time slot. Call :meth:`confirm` to pay and book."""

    def __init__(
        self,
        context: HttpContext,
        active: ActiveReservation,
        licence_id: int,
        examination_type_id: int,
    ) -> None:
        self._context = context
        self._active = active
        self._licence_id = licence_id
        self._examination_type_id = examination_type_id

    @property
    def data(self) -> ActiveReservation:
        return self._active

    @property
    def examination_name(self) -> str:
        return self._active.examination_name

    @property
    def start_date(self) -> datetime:
        return self._active.start_date

    @property
    def expires_at(self) -> datetime:
        return self._active.reservation_expires

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self._active.reservation_expires.replace(
            tzinfo=timezone.utc
        )

    async def get_seconds_remaining(self) -> int:
        """Poll the server for exact seconds left on the hold."""
        body = await self._context.post(
            "get-reservation-time",
            json={
                "expiryDates": [
                    serialize_second_datetime(self._active.reservation_expires)
                ]
            },
        )
        parsed = ReservationTimeResponse(**body)
        logger.debug("Reservation time remaining: %d seconds", parsed.data)
        return parsed.data

    async def get_payment_info(self) -> ReservationInformationData:
        """Fetch cost breakdown, rescheduling info, and payment options."""
        body = await self._context.post(
            "reservation-information",
            json={
                "bookingSession": self._context.booking_session(
                    self._licence_id,
                    examination_type_id=self._examination_type_id,
                ),
            },
        )
        parsed = ReservationInformationResponse(**body)
        logger.debug(
            "Fetched reservation information for licence_id=%d", self._licence_id
        )
        return parsed.data

    async def confirm(self) -> BookingConfirmation:
        """Pay by invoice and confirm the booking."""
        res_info = await self.get_payment_info()

        body = await self._context.post(
            "invoice-payment",
            json={
                "bookingSession": self._context.booking_session(
                    self._licence_id,
                    examination_type_id=self._examination_type_id,
                ),
                "bundleReservation": res_info.model_dump(
                    by_alias=True,
                    mode="json",
                ),
            },
        )
        payment = InvoicePaymentResponse(**body).data
        logger.info(
            "Invoice payment: success=%s, booking_id=%s",
            payment.success,
            payment.booking_id,
        )

        body = await self._context.post(
            "summary",
            json={
                "socialSecurityNumber": self._context.personal_identity_number,
                "bookingId": payment.booking_id,
                "licenceId": self._licence_id,
            },
        )
        summary_data = SummaryResponse(**body).data
        logger.debug(
            "Summary: %d confirmed, %d cancelled",
            len(summary_data.confirmed_examinations),
            len(summary_data.cancelled_examinations),
        )
        return BookingConfirmation(payment.booking_id, summary_data)

    def __repr__(self) -> str:
        return (
            f"Reservation({self.examination_name!r}, "
            f"starts={self.start_date}, expires={self.expires_at})"
        )


class BookingConfirmation:
    """Result of a confirmed booking."""

    def __init__(self, booking_id: str, summary: SummaryData) -> None:
        self._booking_id = booking_id
        self._summary = summary

    @property
    def booking_id(self) -> str:
        return self._booking_id

    @property
    def data(self) -> SummaryData:
        return self._summary

    @property
    def confirmed_examinations(self) -> list[Examination]:
        return self._summary.confirmed_examinations

    @property
    def cancelled_examinations(self) -> list[Examination]:
        return self._summary.cancelled_examinations

    def __repr__(self) -> str:
        return (
            f"BookingConfirmation(id={self._booking_id!r}, "
            f"confirmed={len(self.confirmed_examinations)}, "
            f"cancelled={len(self.cancelled_examinations)})"
        )
