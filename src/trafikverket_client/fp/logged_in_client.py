from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from aiohttp import ClientSession

from ._temporal import serialize_iso_datetime, serialize_second_datetime
from .models import (
    ActiveReservationsData,
    ActiveReservationsResponse,
    BookingHindrancesData,
    BookingHindrancesResponse,
    ConfirmedExaminationsResponse,
    CreateReservationResponse,
    LicenceInformationData,
    LicenceInformationResponse,
    OccasionBundle,
    OccasionBundlesData,
    OccasionBundlesResponse,
    ReservationInformationData,
    ReservationInformationResponse,
    ReservationTimeResponse,
    SearchInformationData,
    SearchInformationResponse,
    SuggestedReservation,
    SignOutResponse,
    StartData,
    StartResponse,
    SuggestedReservationsResponse,
    SystemUpdatingData,
    SystemUpdatingResponse,
)
from .exceptions import NotLoggedInError
from .licence_information import LicenceInformation

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .loginable import Loginable


def _booking_session(
    personal_identity_number: str,
    licence_id: int,
    booking_mode_id: int = 0,
    examination_type_id: int = 0,
    searched_months: int = 0,
) -> dict:
    return {
        "socialSecurityNumber": personal_identity_number,
        "licenceId": licence_id,
        "bookingModeId": booking_mode_id,
        "ignoreDebt": False,
        "ignoreBookingHindrance": False,
        "examinationTypeId": examination_type_id,
        "excludeExaminationCategories": [],
        "rescheduleTypeId": 0,
        "paymentIsActive": False,
        "paymentReference": "",
        "paymentUrl": "",
        "searchedMonths": searched_months,
    }


class LoggedinClient:
    def __init__(
        self, session: ClientSession, loginable: Loginable, user_agent: str
    ) -> None:
        if not loginable.is_logged_in:
            raise NotLoggedInError(
                "LoggedinClient requires a Loginable that has completed BankID"
            )
        self._session = session
        self._user_agent = user_agent
        assert loginable.logged_in_as is not None
        self._personal_identity_number: str = loginable.logged_in_as

    async def close(self) -> None:
        await self.sign_out()
        await self._session.close()

    async def __aenter__(self) -> "LoggedinClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    @property
    def personal_identity_number(self) -> str:
        return self._personal_identity_number

    async def start(self) -> StartData:
        response = await self._session.post(
            "https://fp.trafikverket.se/Boka/start",
            headers={
                "User-Agent": self._user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://fp.trafikverket.se",
                "Connection": "keep-alive",
                "Referer": "https://fp.trafikverket.se/Boka/ng/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Content-Type": "text/plain",
            },
            data="null",
        )
        response.raise_for_status()
        parsed = StartResponse(**await response.json())
        logger.debug("Fetched start config, version=%s", parsed.data.version)
        return parsed.data

    async def sign_out(self) -> None:
        response = await self._session.post(
            "https://fp.trafikverket.se/Boka/sign-out",
            headers={
                "User-Agent": self._user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://fp.trafikverket.se",
                "Connection": "keep-alive",
                "Referer": "https://fp.trafikverket.se/Boka/ng/licence",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Content-Type": "text/plain",
            },
            data="null",
        )
        response.raise_for_status()
        SignOutResponse(**await response.json())
        logger.info("Signed out")

    async def licence_information(self) -> LicenceInformation:
        data = await self._licence_information_raw()
        return LicenceInformation(self, data)

    async def _licence_information_raw(self) -> LicenceInformationData:
        response = await self._session.post(
            "https://fp.trafikverket.se/Boka/licence-information",
            headers={
                "User-Agent": self._user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://fp.trafikverket.se",
                "Connection": "keep-alive",
                "Referer": "https://fp.trafikverket.se/Boka/ng/licence",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Content-Type": "text/plain",
            },
            data="null",
        )
        response.raise_for_status()
        parsed = LicenceInformationResponse(**await response.json())
        logger.debug(
            "Fetched licence information, %d categories",
            len(parsed.data.licence_categories),
        )
        return parsed.data

    async def get_active_reservations(self) -> ActiveReservationsData:
        response = await self._session.post(
            "https://fp.trafikverket.se/Boka/get-active-reservations",
            headers={
                "User-Agent": self._user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://fp.trafikverket.se",
                "Connection": "keep-alive",
                "Referer": "https://fp.trafikverket.se/Boka/ng/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Content-Type": "text/plain",
            },
            data="null",
        )
        response.raise_for_status()
        parsed = ActiveReservationsResponse(**await response.json())
        logger.debug("Fetched active reservations")
        return parsed.data

    async def get_confirmed_examinations(self, licence_id: int) -> list[dict]:
        response = await self._session.post(
            "https://fp.trafikverket.se/Boka/get-confirmed-examinations",
            headers={
                "User-Agent": self._user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://fp.trafikverket.se",
                "Connection": "keep-alive",
                "Referer": "https://fp.trafikverket.se/Boka/ng/licence",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Content-Type": "application/json; charset=utf-8",
            },
            json={"licenceId": licence_id},
        )
        response.raise_for_status()
        parsed = ConfirmedExaminationsResponse(**await response.json())
        logger.debug("Fetched confirmed examinations for licence_id=%d", licence_id)
        return parsed.data

    async def booking_hindrances(
        self,
        licence_id: int,
        booking_mode_id: int = 0,
        examination_type_id: int = 0,
    ) -> BookingHindrancesData:
        response = await self._session.post(
            "https://fp.trafikverket.se/Boka/booking-hindrances",
            headers={
                "User-Agent": self._user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://fp.trafikverket.se",
                "Connection": "keep-alive",
                "Referer": "https://fp.trafikverket.se/Boka/ng/licence",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Content-Type": "application/json; charset=utf-8",
                "Priority": "u=0",
            },
            json={
                "bookingSession": _booking_session(
                    self._personal_identity_number,
                    licence_id,
                    booking_mode_id,
                    examination_type_id,
                ),
            },
        )
        response.raise_for_status()
        parsed = BookingHindrancesResponse(**await response.json())
        logger.debug(
            "Booking hindrances for licence_id=%d: can_book=%s",
            licence_id,
            parsed.data.can_book_licence,
        )
        return parsed.data

    async def get_suggested_reservations(
        self, licence_id: int
    ) -> list[SuggestedReservation] | None:
        response = await self._session.post(
            "https://fp.trafikverket.se/Boka/get-suggested-reservations-by-licence-and-ssn",
            headers={
                "User-Agent": self._user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://fp.trafikverket.se",
                "Connection": "keep-alive",
                "Referer": "https://fp.trafikverket.se/Boka/ng/licence",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Content-Type": "application/json; charset=utf-8",
                "Priority": "u=0",
            },
            json={"licenceId": licence_id, "ssn": self._personal_identity_number},
        )
        response.raise_for_status()
        parsed = SuggestedReservationsResponse(**await response.json())
        logger.debug("Fetched suggested reservations for licence_id=%d", licence_id)
        return parsed.data

    async def search_information(
        self,
        licence_id: int,
        examination_type_id: int = 0,
        booking_mode_id: int = 0,
    ) -> SearchInformationData:
        response = await self._session.post(
            "https://fp.trafikverket.se/Boka/search-information",
            headers={
                "User-Agent": self._user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://fp.trafikverket.se",
                "Connection": "keep-alive",
                "Referer": "https://fp.trafikverket.se/Boka/ng/licence",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Content-Type": "application/json; charset=utf-8",
                "Priority": "u=0",
            },
            json={
                "bookingSession": _booking_session(
                    self._personal_identity_number,
                    licence_id,
                    booking_mode_id,
                    examination_type_id,
                ),
            },
        )
        response.raise_for_status()
        parsed = SearchInformationResponse(**await response.json())
        logger.debug(
            "Fetched search information for licence_id=%d, %d locations",
            licence_id,
            len(parsed.data.locations),
        )
        return parsed.data

    async def occasion_bundles(
        self,
        licence_id: int,
        examination_type_id: int,
        location_id: int,
        start_date: datetime,
        booking_mode_id: int = 0,
        searched_months: int = 0,
        nearby_location_ids: list[int] | None = None,
        language_id: int = 13,
        vehicle_type_id: int = 1,
        tachograph_type_id: int = 1,
        occasion_choice_id: int = 1,
    ) -> OccasionBundlesData:
        response = await self._session.post(
            "https://fp.trafikverket.se/Boka/occasion-bundles",
            headers={
                "User-Agent": self._user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://fp.trafikverket.se",
                "Connection": "keep-alive",
                "Referer": "https://fp.trafikverket.se/Boka/ng/licence",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Content-Type": "application/json; charset=utf-8",
                "Priority": "u=0",
            },
            json={
                "bookingSession": _booking_session(
                    self._personal_identity_number,
                    licence_id,
                    booking_mode_id,
                    examination_type_id,
                    searched_months,
                ),
                "occasionBundleQuery": {
                    "startDate": serialize_iso_datetime(start_date),
                    "searchedMonths": searched_months,
                    "locationId": location_id,
                    "nearbyLocationIds": nearby_location_ids or [],
                    "languageId": language_id,
                    "vehicleTypeId": vehicle_type_id,
                    "tachographTypeId": tachograph_type_id,
                    "occasionChoiceId": occasion_choice_id,
                    "examinationTypeId": examination_type_id,
                },
            },
        )
        response.raise_for_status()
        parsed = OccasionBundlesResponse(**await response.json())
        logger.debug(
            "Fetched occasion bundles for location_id=%d, %d bundles",
            location_id,
            len(parsed.data.bundles),
        )
        return parsed.data

    async def is_system_updating(self) -> SystemUpdatingData:
        response = await self._session.post(
            "https://fp.trafikverket.se/Boka/is-system-updating",
            headers={
                "User-Agent": self._user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://fp.trafikverket.se",
                "Connection": "keep-alive",
                "Referer": "https://fp.trafikverket.se/Boka/ng/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Content-Type": "text/plain",
            },
            data="null",
        )
        response.raise_for_status()
        parsed = SystemUpdatingResponse(**await response.json())
        logger.debug("is_system_updating=%s", parsed.data.is_updating)
        return parsed.data

    async def create_reservation(
        self,
        licence_id: int,
        examination_type_id: int,
        occasion_bundle: OccasionBundle,
        booking_mode_id: int = 0,
    ) -> None:
        response = await self._session.post(
            "https://fp.trafikverket.se/Boka/create-reservation",
            headers={
                "User-Agent": self._user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://fp.trafikverket.se",
                "Connection": "keep-alive",
                "Referer": "https://fp.trafikverket.se/Boka/ng/licence",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Content-Type": "application/json; charset=utf-8",
                "Priority": "u=0",
            },
            json={
                "bookingSession": _booking_session(
                    self._personal_identity_number,
                    licence_id,
                    booking_mode_id,
                    examination_type_id,
                ),
                "occasionBundle": occasion_bundle.model_dump(
                    by_alias=True,
                    mode="json",
                ),
            },
        )
        response.raise_for_status()
        CreateReservationResponse(**await response.json())
        logger.info("Created reservation for licence_id=%d", licence_id)

    async def reservation_information(
        self,
        licence_id: int,
        examination_type_id: int,
        booking_mode_id: int = 0,
    ) -> ReservationInformationData:
        response = await self._session.post(
            "https://fp.trafikverket.se/Boka/reservation-information",
            headers={
                "User-Agent": self._user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://fp.trafikverket.se",
                "Connection": "keep-alive",
                "Referer": "https://fp.trafikverket.se/Boka/ng/licence",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Content-Type": "application/json; charset=utf-8",
                "Priority": "u=0",
            },
            json={
                "bookingSession": _booking_session(
                    self._personal_identity_number,
                    licence_id,
                    booking_mode_id,
                    examination_type_id,
                ),
            },
        )
        response.raise_for_status()
        parsed = ReservationInformationResponse(**await response.json())
        logger.debug("Fetched reservation information for licence_id=%d", licence_id)
        return parsed.data

    async def get_reservation_time(self, expiry_dates: list[datetime]) -> int:
        response = await self._session.post(
            "https://fp.trafikverket.se/Boka/get-reservation-time",
            headers={
                "User-Agent": self._user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://fp.trafikverket.se",
                "Connection": "keep-alive",
                "Referer": "https://fp.trafikverket.se/Boka/ng/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Content-Type": "application/json; charset=utf-8",
            },
            json={
                "expiryDates": [
                    serialize_second_datetime(expiry) for expiry in expiry_dates
                ]
            },
        )
        response.raise_for_status()
        parsed = ReservationTimeResponse(**await response.json())
        logger.debug("Reservation time remaining: %d seconds", parsed.data)
        return parsed.data
