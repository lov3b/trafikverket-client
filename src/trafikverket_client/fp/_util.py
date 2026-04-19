from __future__ import annotations

from typing import Any

from aiohttp import ClientResponse

from .exceptions import ApiError


async def parse_json(response: ClientResponse) -> dict[str, Any]:
    """Check HTTP status, read JSON, and verify the API-level status field."""
    response.raise_for_status()
    body = await response.json()
    status = body.get("status")
    if isinstance(status, int) and status != 200:
        raise ApiError(status, body)
    return body
