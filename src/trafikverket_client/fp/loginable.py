from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Optional

from aiohttp import ClientSession

from .models import (
    AuthenticationData,
    AuthenticationStatusResponse,
    BankIdExceptionResponse,
    IsAuthorizedResponse,
)
from .qr import ShowQr, make_bankid_qr_payload, make_qr_renderer
from .exceptions import BankidStop

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .logged_in_client import LoggedinClient


class Loginable:
    def __init__(
        self,
        session: ClientSession,
        authentication_data: AuthenticationData,
        user_agent: str,
        logged_in_as: Optional[str] = None,
        show_qr: ShowQr = ShowQr.AUTO,
    ) -> None:
        self._session = session
        self._authentication_data = authentication_data
        self._user_agent = user_agent
        self._logged_in_as = logged_in_as
        self._show_qr = show_qr

    @property
    def authentication_data(self) -> AuthenticationData:
        """Exposed so a UI can render/refresh the QR on each poll."""
        return self._authentication_data

    @property
    def is_logged_in(self) -> bool:
        return bool(self._logged_in_as)

    @property
    def logged_in_as(self) -> Optional[str]:
        """SSN the backend reports once BankID completes. ``None`` while pending."""
        return self._logged_in_as

    async def check(self) -> "Loginable":
        """Poll the QR status."""
        response = await self._session.post(
            "https://fp.trafikverket.se/Boka/check-authentication-status-qr",
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
                "referenceId": self._authentication_data.reference_id,
                "qrStartToken": self._authentication_data.qr_start_token,
                "qrStartTime": self._authentication_data.qr_start_time,
                "qrStartSecret": self._authentication_data.qr_start_secret,
            },
        )
        response.raise_for_status()
        body = await response.json()

        if body.get("status") == 400:
            error = BankIdExceptionResponse(**body)
            logger.warning("BankID flow aborted: %s", error.data.message)
            raise BankidStop(error.data.message)

        parsed = AuthenticationStatusResponse(**body)
        if parsed.data.login_status:
            logger.info("BankID authentication completed")
        else:
            logger.debug(
                "BankID polling, collection_status=%s", parsed.data.collection_status
            )
        return Loginable(
            session=self._session,
            authentication_data=self._authentication_data,
            user_agent=self._user_agent,
            logged_in_as=parsed.data.login_status,
            show_qr=self._show_qr,
        )

    async def wait_until_logged_in(
        self,
        poll_interval_seconds: float = 2.0,
        timeout_seconds: float = 180.0,
    ) -> "Loginable":
        """Poll ``check`` until ``loginStatus`` is set."""
        qr = make_qr_renderer(self._show_qr)

        async def _loop() -> "Loginable":
            current: Loginable = self
            while not current.is_logged_in:
                qr.update(
                    make_bankid_qr_payload(
                        current.authentication_data.qr_start_token,
                        current.authentication_data.qr_start_secret,
                        current.authentication_data.qr_start_time,
                    )
                )
                await asyncio.sleep(poll_interval_seconds)
                current = await current.check()
            return current

        return await asyncio.wait_for(_loop(), timeout=timeout_seconds)

    def into_client(self) -> "LoggedinClient":
        """Convert this completed login into a :class:`LoggedinClient`."""
        from .logged_in_client import LoggedinClient

        return LoggedinClient(self._session, self, self._user_agent)

    async def is_authorized(self) -> bool:
        """Ask the backend whether the session cookie is still authorized."""
        response = await self._session.post(
            "https://fp.trafikverket.se/Boka/is-authorizied",
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
        parsed = IsAuthorizedResponse(**await response.json())
        logger.debug("is_authorized=%s", parsed.data)
        return parsed.data
