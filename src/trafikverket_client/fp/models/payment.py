from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator
from pydantic.alias_generators import to_camel

from .._temporal import parse_iso_datetime
from .examination import Examination


class PaymentHistoryItem(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    order_item_id: int
    reference_id: str
    product_name: str
    product_description: str
    order_item_date: datetime
    order_item_date_str: str
    order_date: datetime
    order_item_print_date: Optional[str] = None
    initial_amount: float
    reminder_fee_amount: float
    is_pending_payment: bool
    is_paid: bool
    paid_amount: float
    remaining_amount_to_pay: float
    paid_amount_direct: float
    paid_amount_balance: float
    paid_amount_invoice: float
    direct_payment_method: Optional[str] = None
    invoice_expiry_date: Optional[datetime] = None
    invoice_expiry_date_str: str
    invoice_paid_date_str: Optional[str] = None
    invoice_reminder_date: Optional[datetime] = None
    invoice_recovery_date: Optional[datetime] = None
    invoice_create_date: Optional[datetime] = None
    original_invoice_expiry_date: Optional[datetime] = None
    is_invoice: bool
    is_invoice_expired: bool
    invoice_id: Optional[int] = None
    is_cancelled_in_time: bool
    is_cancelled_late: bool
    is_automatic_with_refund: bool
    is_automatic_without_refund: bool
    is_all_product_selections_refunded: bool
    cancelled_date: Optional[datetime] = None
    is_reminder_sent: bool
    is_recovery_sent: bool
    is_recovery_withdrawn: bool
    is_cancelled_and_valid: bool
    pab_examination_id: int
    printed_document_id: Optional[int] = None
    booking_confirmation: Optional[str] = None
    ocr_code: str
    is_selected: bool
    examination_result_id: int
    examination_model: Examination

    @field_validator(
        "order_item_date",
        "order_date",
        "invoice_expiry_date",
        "invoice_reminder_date",
        "invoice_recovery_date",
        "invoice_create_date",
        "original_invoice_expiry_date",
        "cancelled_date",
        mode="before",
    )
    @classmethod
    def _parse_datetimes(cls, value: object) -> datetime | None:
        if value is None:
            return None
        return parse_iso_datetime(value)


class PaymentModelData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    has_debt: bool
    unpaid_amount: float
    available_balance: float
    locked_balance: float
    unpaid_history_models: list[PaymentHistoryItem]
    paid_history_models: list[PaymentHistoryItem]
    fully_paid_with_balance_this_session: list[PaymentHistoryItem]
    use_direct_payment: bool
    new_payment_reference: str
    active_payment: Optional[dict[str, object]] = None


class PaymentModelResponse(BaseModel):
    data: PaymentModelData
    status: int
    url: HttpUrl
