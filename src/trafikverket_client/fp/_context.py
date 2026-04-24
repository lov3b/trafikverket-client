from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientSession

from .exceptions import ApiError

logger = logging.getLogger(__name__)

_BASE = "https://fp.trafikverket.se/Boka"

_SENTINEL = object()


class HttpContext:
    """Shared HTTP state for all post-login API calls."""

    __slots__ = ("session", "user_agent", "personal_identity_number")

    def __init__(
        self,
        session: ClientSession,
        user_agent: str,
        personal_identity_number: str,
    ) -> None:
        self.session = session
        self.user_agent = user_agent
        self.personal_identity_number = personal_identity_number

    async def post(self, path: str, *, json: Any = _SENTINEL) -> dict[str, Any]:
        """POST to ``/Boka/{path}`` and return parsed, status-checked JSON."""
        url = f"{_BASE}/{path}"
        if json is _SENTINEL:
            headers = self._headers("text/plain")
            response = await self.session.post(url, headers=headers, data="null")
        else:
            headers = self._headers("application/json; charset=utf-8")
            response = await self.session.post(url, headers=headers, json=json)

        response.raise_for_status()
        body = await response.json()
        status = body.get("status")
        if isinstance(status, int) and status != 200:
            raise ApiError(status, body)
        return body

    def booking_session(
        self,
        licence_id: int,
        booking_mode_id: int = 0,
        examination_type_id: int = 0,
        searched_months: int = 0,
    ) -> dict[str, Any]:
        return {
            "socialSecurityNumber": self.personal_identity_number,
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

    async def close(self) -> None:
        from .models import SignOutResponse

        body = await self.post("sign-out")
        SignOutResponse(**body)
        logger.info("Signed out")
        await self.session.close()

    def _headers(self, content_type: str) -> dict[str, str]:
        return {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://fp.trafikverket.se",
            "Connection": "keep-alive",
            "Referer": "https://fp.trafikverket.se/Boka/ng/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Content-Type": content_type,
        }
