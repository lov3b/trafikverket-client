from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from .._temporal import serialize_iso_datetime
from ..models import (
    ExaminationType,
    Location,
    LocationEntry,
    OccasionBundlesResponse,
    SearchInformationData,
)

if TYPE_CHECKING:
    from .._context import HttpContext
    from .slot import SlotList

logger = logging.getLogger(__name__)


class SearchResult:
    """Wraps search-information data and provides access to available slots."""

    def __init__(
        self,
        context: HttpContext,
        data: SearchInformationData,
        licence_id: int,
        examination_type_id: int,
    ) -> None:
        self._context = context
        self._data = data
        self._licence_id = licence_id
        self._examination_type_id = examination_type_id

    @property
    def data(self) -> SearchInformationData:
        return self._data

    @property
    def locations(self) -> list[LocationEntry]:
        return self._data.locations

    @property
    def examination_types(self) -> list[ExaminationType]:
        return self._data.examination_types

    async def get_available_slots(
        self,
        location: Location | int,
        start_date: datetime | None = None,
        *,
        searched_months: int = 0,
        nearby_location_ids: list[int] | None = None,
        language_id: int = 13,
        vehicle_type_id: int = 1,
        tachograph_type_id: int = 1,
        occasion_choice_id: int = 1,
    ) -> SlotList:
        from .slot import SlotList

        location_id = location if isinstance(location, int) else location.id
        if start_date is None:
            start_date = datetime.now(timezone.utc)

        body = await self._context.post(
            "occasion-bundles",
            json={
                "bookingSession": self._context.booking_session(
                    self._licence_id,
                    examination_type_id=self._examination_type_id,
                    searched_months=searched_months,
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
                    "examinationTypeId": self._examination_type_id,
                },
            },
        )
        parsed = OccasionBundlesResponse(**body)
        logger.debug(
            "Fetched occasion bundles for location_id=%d, %d bundles",
            location_id,
            len(parsed.data.bundles),
        )
        return SlotList(
            context=self._context,
            data=parsed.data,
            licence_id=self._licence_id,
            examination_type_id=self._examination_type_id,
        )
