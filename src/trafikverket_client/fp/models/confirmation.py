from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl
from pydantic.alias_generators import to_camel

from .examination import Examination


class ExaminationsToCancelData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    show_24_hour_cancellation_warning: bool
    show_multiple_examinations_warning: bool
    examinations: list[Examination]


class ExaminationsToCancelResponse(BaseModel):
    data: ExaminationsToCancelData
    status: int
    url: HttpUrl


class ConfirmCancelResponse(BaseModel):
    data: None = None
    status: int
    url: HttpUrl


class InvoicePaymentData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    success: bool
    is_cancelled: bool
    booking_id: str
    is_reservation: bool
    is_signed_in: bool
    message: Optional[str] = None
    personal_identity_number: Optional[str] = None
    licence_id: int
    reservation_time_in_seconds: int


class InvoicePaymentResponse(BaseModel):
    data: InvoicePaymentData
    status: int
    url: HttpUrl


class SummaryData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    confirmed_examinations: list[Examination]
    cancelled_examinations: list[Examination]
    information: str
    show_risk_education_warning: bool
    show_photo_warning: bool
    is_calendar_enabled: bool
    provider_logo_path: Optional[str] = None
    show_underaged_warning: bool
    add_prepaid_photo_fee: bool
    prepaid_photo_fee_is_paid: bool
    prepaid_photo_fee_cost: float


class SummaryResponse(BaseModel):
    data: SummaryData
    status: int
    url: HttpUrl
