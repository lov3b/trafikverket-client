from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl
from pydantic.alias_generators import to_camel


class AuthenticationData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    reference_id: str
    autostart_token: str
    qr_start_token: str
    qr_start_secret: str
    qr_start_time: int
    qr_code: str


class AuthenticationResponse(BaseModel):
    data: AuthenticationData
    status: int
    url: HttpUrl


class AuthenticationStatusData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    qr_code: str
    collection_status: str
    login_status: Optional[str] = None


class AuthenticationStatusResponse(BaseModel):
    data: AuthenticationStatusData
    status: int
    url: HttpUrl


class StartData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    login_required: bool
    bank_id_login_required: bool
    # Null until the user has logged in; nullable on the wire.
    booking_count: Optional[int] = None
    unpaid_count: Optional[int] = None
    refund_enabled: bool
    use_direct_payment: bool
    otp_enabled: bool
    continue_without_login_enabled: bool
    hcaptcha_enabled_on_otp: bool
    hcaptcha_site_key: str
    global_message: str
    is_mobile: bool
    version: str


class StartResponse(BaseModel):
    data: StartData
    status: int
    url: HttpUrl


class IsAuthorizedResponse(BaseModel):
    data: bool
    status: int
    url: HttpUrl


class SignOutResponse(BaseModel):
    data: Optional[None] = None
    status: int
    url: HttpUrl


class BankIdExceptionData(BaseModel):
    message: str
    success: bool


class BankIdExceptionResponse(BaseModel):
    status: int
    data: BankIdExceptionData
    type: str
