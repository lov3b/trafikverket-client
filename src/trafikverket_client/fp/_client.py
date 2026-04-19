from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiohttp import ClientSession, ClientTimeout

from ._util import parse_json
from .models import AuthenticationResponse
from .qr import ShowQr

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .logged_in_client import LoggedinClient
    from .loginable import Loginable


class Client:
    def __init__(
        self,
        user_agent: str = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/146.0.0.0 Safari/537.36"
        ),
        timeout_seconds: int = 30,
    ) -> None:
        self._session = ClientSession(timeout=ClientTimeout(total=timeout_seconds))
        self._user_agent = user_agent
        self._timeout_seconds = timeout_seconds

    async def close(self) -> None:
        await self._session.close()

    async def __aenter__(self) -> "Client":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def login(
        self,
        show_qr: ShowQr = ShowQr.AUTO,
        poll_interval_seconds: float = 2.0,
        timeout_seconds: float = 180.0,
    ) -> "LoggedinClient":
        """Log in via BankID and return a ready-to-use :class:`LoggedinClient`."""
        loginable = await self.begin_login(show_qr=show_qr)
        done = await loginable.wait_until_logged_in(
            poll_interval_seconds=poll_interval_seconds,
            timeout_seconds=timeout_seconds,
        )
        return done.into_client()

    async def begin_login(
        self,
        show_qr: ShowQr = ShowQr.AUTO,
    ) -> "Loginable":
        """Kick off BankID QR authentication."""
        from .loginable import Loginable

        logger.debug("Starting BankID authentication")
        response = await self._session.post(
            "https://fp.trafikverket.se/Boka/begin-authentication",
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
                "Priority": "u=0",
            },
            data="null",
        )
        body = await parse_json(response)
        parsed = AuthenticationResponse(**body)
        logger.debug(
            "BankID authentication started, reference_id=%s", parsed.data.reference_id
        )
        return Loginable(
            session=self._session,
            authentication_data=parsed.data,
            user_agent=self._user_agent,
            show_qr=show_qr,
        )
