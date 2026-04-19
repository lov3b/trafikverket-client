from __future__ import annotations

from datetime import date, datetime, time


def parse_iso_datetime(value: object) -> datetime:
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        raise TypeError(
            f"Expected datetime or ISO datetime string, got {type(value)!r}"
        )
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_datetime_format(value: object, fmt: str) -> datetime:
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        raise TypeError(f"Expected datetime or datetime string, got {type(value)!r}")
    return datetime.strptime(value, fmt)


def parse_date_value(value: object) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise TypeError(f"Expected date or date string, got {type(value)!r}")
    return date.fromisoformat(value)


def parse_optional_date_value(value: object) -> date | None:
    if value in (None, ""):
        return None
    return parse_date_value(value)


def parse_time_value(value: object) -> time:
    if isinstance(value, time):
        return value
    if not isinstance(value, str):
        raise TypeError(f"Expected time or time string, got {type(value)!r}")
    return time.fromisoformat(value)


def serialize_iso_datetime(value: datetime) -> str:
    return value.isoformat()


def serialize_minute_datetime(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M")


def serialize_second_datetime(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S")


def serialize_time_hm(value: time) -> str:
    return value.strftime("%H:%M")
