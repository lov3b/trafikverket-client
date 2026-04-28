from __future__ import annotations

import logging

from ._context import HttpContext
from .licence_information import LicenceInformation
from .models import (
    ActiveReservationsResponse,
    ExaminationsResponse,
    InformationData,
    InformationResponse,
    LicenceInformationResponse,
    PaymentModelData,
    PaymentModelResponse,
    SystemUpdatingData,
    SystemUpdatingResponse,
)
from .views import ExaminationList, Reservation

logger = logging.getLogger(__name__)


class Session:
    """User-facing session returned by :meth:`Client.login`.

    Provides a high-level, object-oriented API over the Trafikverket
    booking system.  Every method returns a domain object that knows
    what actions are available next.
    """

    def __init__(self, context: HttpContext) -> None:
        self._context = context

    async def close(self) -> None:
        await self._context.close()

    async def __aenter__(self) -> Session:
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        await self.close()

    @property
    def personal_identity_number(self) -> str:
        return self._context.personal_identity_number

    async def get_licences(self) -> LicenceInformation:
        body = await self._context.post("licence-information")
        parsed = LicenceInformationResponse(**body)
        logger.debug(
            "Fetched licence information, %d categories",
            len(parsed.data.licence_categories),
        )
        return LicenceInformation(self._context, parsed.data)

    async def get_examinations(self) -> ExaminationList:
        body = await self._context.post("examinations")
        parsed = ExaminationsResponse(**body)
        logger.debug(
            "Fetched examinations: %d confirmed, %d completed",
            len(parsed.data.confirmed_examinations),
            len(parsed.data.completed_examinations),
        )
        return ExaminationList(self._context, parsed.data)

    async def get_active_reservations(self) -> list[Reservation]:
        body = await self._context.post("get-active-reservations")
        parsed = ActiveReservationsResponse(**body)
        logger.debug("Fetched active reservations")
        return [
            Reservation(
                context=self._context,
                active=ar,
                licence_id=ar.licence_id,
                examination_type_id=ar.examination_type_id,
            )
            for ar in parsed.data.active_reservations or []
        ]

    async def get_aspirant_info(self) -> InformationData:
        body = await self._context.post("information")
        parsed = InformationResponse(**body)
        logger.debug("Fetched aspirant information: %s", parsed.data.aspirant.name)
        return parsed.data

    async def get_payment_model(self) -> PaymentModelData:
        body = await self._context.post(
            "GetPaymentModel", json={"directPaymentReferenceId": None}
        )
        parsed = PaymentModelResponse(**body)
        logger.debug(
            "Fetched payment model: has_debt=%s, balance=%.2f",
            parsed.data.has_debt,
            parsed.data.available_balance,
        )
        return parsed.data

    async def get_system_status(self) -> SystemUpdatingData:
        body = await self._context.post("is-system-updating")
        parsed = SystemUpdatingResponse(**body)
        logger.debug("is_system_updating=%s", parsed.data.is_updating)
        return parsed.data
