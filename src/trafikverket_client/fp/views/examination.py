from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ..models import (
    ConfirmCancelResponse,
    Examination,
    ExaminationsData,
    ExaminationsToCancelData,
    ExaminationsToCancelResponse,
    SearchInformationResponse,
)

if TYPE_CHECKING:
    from .._context import HttpContext
    from .search_result import SearchResult

logger = logging.getLogger(__name__)


class ExaminationView:
    """Wraps a single examination with cancel/rebook actions."""

    def __init__(self, context: HttpContext, exam: Examination) -> None:
        self._context = context
        self._exam = exam

    @property
    def data(self) -> Examination:
        return self._exam

    @property
    def id(self) -> int:
        return self._exam.id

    @property
    def name(self) -> str:
        return self._exam.name

    @property
    def start_date(self) -> str:
        return self._exam.start_date

    @property
    def can_cancel(self) -> bool:
        return self._exam.can_cancel

    @property
    def can_reschedule(self) -> bool:
        return self._exam.can_reschedule

    async def cancel_preview(self) -> CancelPreview:
        """Preview what will be cancelled, with warnings."""
        body = await self._context.post(
            "examinations-to-cancel",
            json={"examinationId": self._exam.id},
        )
        parsed = ExaminationsToCancelResponse(**body)
        logger.debug(
            "Examinations to cancel for id=%d: %d examinations",
            self._exam.id,
            len(parsed.data.examinations),
        )
        return CancelPreview(self._context, self._exam.id, parsed.data)

    async def cancel(self) -> None:
        """Cancel this examination immediately."""
        body = await self._context.post(
            "confirm-cancel",
            json={"examinationId": self._exam.id},
        )
        ConfirmCancelResponse(**body)
        logger.info("Cancelled examination id=%d", self._exam.id)

    async def rebook(self, examination_type_id: int | None = None) -> SearchResult:
        """Enter the rebooking flow. Returns a SearchResult to find new slots."""
        from .search_result import SearchResult

        exam_type_id = examination_type_id or self._exam.examination_type_id
        body = await self._context.post(
            "search-information",
            json={
                "bookingSession": self._context.booking_session(
                    self._exam.licence_id,
                    examination_type_id=exam_type_id,
                ),
            },
        )
        parsed = SearchInformationResponse(**body)
        logger.debug(
            "Fetched search information for licence_id=%d, %d locations",
            self._exam.licence_id,
            len(parsed.data.locations),
        )
        return SearchResult(
            context=self._context,
            data=parsed.data,
            licence_id=self._exam.licence_id,
            examination_type_id=exam_type_id,
        )

    def __repr__(self) -> str:
        return (
            f"ExaminationView({self._exam.name!r}, "
            f"id={self._exam.id}, start={self._exam.start_date})"
        )


class CancelPreview:
    """Preview of an examination cancellation."""

    def __init__(
        self,
        context: HttpContext,
        examination_id: int,
        data: ExaminationsToCancelData,
    ) -> None:
        self._context = context
        self._examination_id = examination_id
        self._data = data

    @property
    def data(self) -> ExaminationsToCancelData:
        return self._data

    @property
    def examinations(self) -> list[Examination]:
        return self._data.examinations

    @property
    def show_24_hour_warning(self) -> bool:
        return self._data.show_24_hour_cancellation_warning

    async def confirm(self) -> None:
        """Execute the cancellation."""
        body = await self._context.post(
            "confirm-cancel",
            json={"examinationId": self._examination_id},
        )
        ConfirmCancelResponse(**body)
        logger.info("Cancelled examination id=%d", self._examination_id)


class ExaminationList:
    """Wraps the examinations response with filtered views."""

    def __init__(self, context: HttpContext, data: ExaminationsData) -> None:
        self._data = data
        self._confirmed = [
            ExaminationView(context, e) for e in data.confirmed_examinations
        ]
        self._completed = [
            ExaminationView(context, e) for e in data.completed_examinations
        ]

    @property
    def data(self) -> ExaminationsData:
        return self._data

    @property
    def confirmed(self) -> list[ExaminationView]:
        return self._confirmed

    @property
    def completed(self) -> list[ExaminationView]:
        return self._completed

    @property
    def cancellable(self) -> list[ExaminationView]:
        return [e for e in self._confirmed if e.can_cancel]

    @property
    def reschedulable(self) -> list[ExaminationView]:
        return [e for e in self._confirmed if e.can_reschedule]

    def __len__(self) -> int:
        return len(self._confirmed) + len(self._completed)

    def __repr__(self) -> str:
        return (
            f"ExaminationList(confirmed={len(self._confirmed)}, "
            f"completed={len(self._completed)})"
        )
