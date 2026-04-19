from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator
from pydantic.alias_generators import to_camel

from .._temporal import parse_iso_datetime
from .booking import Address, Aspirant, Coordinates, Duration


class ExaminationResult(BaseModel):
    id: int
    name: Optional[str] = None


class ExaminationPlace(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    location_name: str
    information: str
    address: Address
    coordinates: Coordinates
    display_name: str


class ExaminationPaymentInfo(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    amount_to_pay: str
    amount_paid: str
    cost: str
    invoice_expiry_date: str
    has_reminder_fee: bool
    is_sent_to_recovery: bool
    is_paid: bool
    is_fee_removed: bool


class BlobReference(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    blob_type: int
    id: int
    blob_id: Optional[int] = None


class AccentLanguage(BaseModel):
    id: int
    name: Optional[str] = None


class Examination(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    name: str
    licence_id: int
    properties: str
    aspirant_name: str
    aspirant_personal_identity_number: str = Field(
        alias="aspriantSocialSecurityNumber"
    )  # sic — typo is on the wire
    duration: Duration
    place: ExaminationPlace
    add_prepaid_photo_fee: bool
    add_prepaid_photo_fee_mandatory: bool
    status: int
    result: Optional[ExaminationResult] = None
    has_failed_functional_test: bool
    payment_information: ExaminationPaymentInfo
    educator: Optional[str] = None
    log: Optional[str] = None
    documents: Optional[str] = None
    booked_by: str
    hindrances: list[dict[str, object]]
    can_cancel: bool
    can_reschedule: bool
    prohibit_reschedulation: bool  # sic
    booking_confirmation: Optional[BlobReference] = None
    invoice_document_information: Optional[BlobReference] = None
    has_result_document: bool
    result_document: Optional[BlobReference] = None
    is_cancelled: bool
    has_result: bool
    booked_date: datetime
    is_validated: bool
    has_hindrances: bool
    start_date: str
    tachograph_type: int
    examination_type_id: int
    examination_type_code: str
    language_id: int
    accent_language: AccentLanguage
    planning_group: str
    calendar_file_uri: Optional[str] = None
    is_late_cancelled_must_pay: bool
    reference_id: str
    can_view_electric_allergy: bool
    is_military: bool
    military_employee_name: Optional[str] = None
    occasion_choice: int
    booking_confirmation_url: str
    booking_info_url: str
    booking_hindrance_url: str
    is_theory: bool
    show_examination_type_change_dropdown: bool
    can_change_oral_examination_type: bool
    show_examination_type_change_button: bool
    enable_get_booking_confirmation: bool
    before_examination_enabled: bool
    new_booking_confirmation_enabled: bool
    has_printing_document: bool
    matching_time_stamps: str
    not_possible_reason: int

    @field_validator("booked_date", mode="before")
    @classmethod
    def _parse_booked_date(cls, value: object) -> datetime:
        return parse_iso_datetime(value)


class ExaminationsData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    is_calendar_enabled: bool
    has_confirmed_examinations: bool
    confirmed_examinations: list[Examination]
    has_completed_examinations: bool
    completed_examinations: list[Examination]


class ExaminationsResponse(BaseModel):
    data: ExaminationsData
    status: int
    url: HttpUrl


class InformationData(BaseModel):
    aspirant: Aspirant


class InformationResponse(BaseModel):
    data: InformationData
    status: int
    url: HttpUrl
