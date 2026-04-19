from datetime import date as date_type, datetime, time as time_type
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl, field_serializer, field_validator
from pydantic.alias_generators import to_camel

from .._temporal import (
    parse_date_value,
    parse_datetime_format,
    parse_iso_datetime,
    parse_optional_date_value,
    parse_time_value,
    serialize_time_hm,
)
from .licence import Licence, LicenceCategoryGroup


class ActiveReservation(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    examination_id: int
    examination_type_id: int
    social_security_number: str
    location_id: int
    vehicle_type_id: int
    language_id: Optional[int] = None
    licence_id: int
    examination_name: str
    examination_category: int
    start_date: datetime
    reservation_expires: datetime
    direct_payment_reference_id: str
    loading: bool
    warnings: list[str]
    add_prepaid_photo_fee: bool
    add_prepaid_photo_fee_mandatory: bool

    @field_validator("start_date", mode="before")
    @classmethod
    def _parse_start_date(cls, value: object) -> datetime:
        return parse_datetime_format(value, "%Y-%m-%d %H:%M")

    @field_validator("reservation_expires", mode="before")
    @classmethod
    def _parse_reservation_expires(cls, value: object) -> datetime:
        return parse_datetime_format(value, "%Y-%m-%d %H:%M:%S")


class SuggestedReservation(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    examination_type_id: int
    licence_id: int
    examination_name: str
    examination_category: int
    suggested_exam_date: date_type
    has_valid: bool
    valid_until: Optional[date_type] = None
    has_taxi_knowledge: bool
    hindrance_ids: list[int]
    has_booking: bool
    can_use_custom_vehicle: bool

    @field_validator("suggested_exam_date", mode="before")
    @classmethod
    def _parse_suggested_exam_date(cls, value: object) -> date_type:
        return parse_date_value(value)

    @field_validator("valid_until", mode="before")
    @classmethod
    def _parse_valid_until(cls, value: object) -> Optional[date_type]:
        return parse_optional_date_value(value)


class ActiveReservationsData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    add_prepaid_photo_fee_possible: bool
    active_reservations: Optional[list[ActiveReservation]] = None
    suggested_reservations: Optional[list[SuggestedReservation]] = None


class ActiveReservationsResponse(BaseModel):
    data: ActiveReservationsData
    status: int
    url: HttpUrl


class ConfirmedExaminationsResponse(BaseModel):
    data: list[dict]
    status: int
    url: HttpUrl


class BookingHindrancesData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    can_book_licence: bool
    hindrance_messages: list[str]
    hindrance_ids: list[int]


class BookingHindrancesResponse(BaseModel):
    data: BookingHindrancesData
    status: int
    url: HttpUrl


class SuggestedReservationsResponse(BaseModel):
    data: Optional[list[SuggestedReservation]] = None
    status: int
    url: HttpUrl


# ===========================================================================
# Search / booking flow models
# ===========================================================================


class Address(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    street_address1: str
    street_address2: str
    zip_code: str
    city: str
    care_of: str


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class Location(BaseModel):
    id: int
    name: str
    address: Address
    coordinates: Coordinates


class ExaminationCategory(BaseModel):
    value: int


class LocationEntry(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    examination_categories: list[ExaminationCategory]
    location: Location


class TimeInterval(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    start_date: datetime
    name: str

    @field_validator("start_date", mode="before")
    @classmethod
    def _parse_start_date(cls, value: object) -> datetime:
        return parse_iso_datetime(value)


class Language(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    name: str
    code: str
    location_ids: list[int]


class VehicleType(BaseModel):
    id: int
    name: str


class TachographType(BaseModel):
    id: int
    name: str


class OccasionChoice(BaseModel):
    id: int
    name: str


class ExaminationType(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    examination_category: int
    name: str


class SearchInformationData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    can_book_licence: bool
    licence_id: int
    licences: list[Licence]
    licence_categories: list[LicenceCategoryGroup]
    location_id: Optional[int] = None
    locations: list[LocationEntry]
    enable_nearby_locations: bool
    max_nearby_locations: int
    nearby_location_ids: Optional[list[int]] = None
    time_interval_id: int
    time_intervals: list[TimeInterval]
    show_language: bool
    language_id: Optional[int] = None
    languages: list[Language]
    show_vehicle_type: bool
    vehicle_type_id: Optional[int] = None
    vehicle_types: list[VehicleType]
    show_tachograph_type: bool
    tachograph_type_id: Optional[int] = None
    tachograph_types: list[TachographType]
    show_occasion_choices: bool
    occasion_choice_id: Optional[int] = None
    occasion_choices: list[OccasionChoice]
    show_examination_type: bool
    examination_types: list[ExaminationType]
    provider_logo_path: Optional[str] = None
    hindrance_message: list[str]
    max_search_period_in_months: int


class SearchInformationResponse(BaseModel):
    data: SearchInformationData
    status: int
    url: HttpUrl


class Duration(BaseModel):
    start: datetime
    end: datetime

    @field_validator("start", "end", mode="before")
    @classmethod
    def _parse_datetimes(cls, value: object) -> datetime:
        return parse_iso_datetime(value)


class Occasion(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    examination_id: Optional[int] = None
    examination_category: int
    duration: Duration
    examination_type_id: int
    location_id: int
    occasion_choice_id: int
    vehicle_type_id: int
    language_id: Optional[int] = None
    tachograph_type_id: int
    name: str
    properties: Optional[str] = None
    date: date_type
    time: time_type
    location_name: str
    cost: str
    cost_text: str
    increased_fee: bool
    is_educator_booking: Optional[bool] = None
    is_late_cancellation: bool
    is_outside_valid_duration: bool
    is_using_taxi_knowledge_valid_duration: bool
    place_address: Optional[str] = None
    place_coordinate: Optional[str] = None

    @field_validator("date", mode="before")
    @classmethod
    def _parse_date(cls, value: object) -> date_type:
        return parse_date_value(value)

    @field_validator("time", mode="before")
    @classmethod
    def _parse_time(cls, value: object) -> time_type:
        return parse_time_value(value)

    @field_serializer("time")
    def _serialize_time(self, value: time_type) -> str:
        return serialize_time_hm(value)


class OccasionBundle(BaseModel):
    occasions: list[Occasion]
    cost: str


class OccasionBundlesData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    bundles: list[OccasionBundle]
    searched_months: int


class OccasionBundlesResponse(BaseModel):
    data: OccasionBundlesData
    status: int
    url: HttpUrl


class SystemUpdatingData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    is_updating: bool
    update_message: str
    show_timer_message: bool
    timer_message: str


class SystemUpdatingResponse(BaseModel):
    data: SystemUpdatingData
    status: int
    url: HttpUrl


class CreateReservationResponse(BaseModel):
    data: Optional[None] = None
    status: int
    url: HttpUrl


class Aspirant(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    age: int
    social_security_number: str
    name: str
    address: Address
    has_protected_identity: bool
    email: Optional[str] = None
    email_exists: bool
    phone: Optional[str] = None
    phone_exists: bool
    verified_phone: bool
    verified_email: bool
    allow_email_surveys: bool
    has_return_mail: bool
    updated_by_partner: bool
    exemptions: list[dict]
    is_deceased: Optional[bool] = None


class PaymentProvider(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    is_pay_direct_payment_enabled: bool
    is_pay_invoice_enabled: bool
    is_pay_balance_enabled: bool
    is_psp_refund_enabled: bool
    logo_path: Optional[str] = None


class ReservationInformationData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    aspirant: Aspirant
    reservations: list[Occasion]
    cancellations: list[dict]
    add_prepaid_photo_fee: bool
    prepaid_photo_fee_cost: float
    is_rescheduling: bool
    show_24_hour_cancellation_warning: bool
    show_24_hour_reservation_warning: bool
    has_balance: bool
    balance_covers_cost: bool
    is_surplus_balance: bool
    show_direct_payment: bool
    amount_to_pay_direct: str
    amount_to_pay_invoice: str
    available_balance: str
    surplus_balance: str
    reservation_time_in_seconds: int
    is_authenticated: bool
    payment_is_active: bool
    active_payment_state: int
    provider: PaymentProvider


class ReservationInformationResponse(BaseModel):
    data: ReservationInformationData
    status: int
    url: HttpUrl


class ReservationTimeResponse(BaseModel):
    data: int
    status: int
    url: HttpUrl
