from datetime import UTC, datetime

from uuid_utils import UUID, uuid7


def current_utc_timestamp() -> int:
    return round(datetime.now(UTC).timestamp())


def timestamp_after_delta(hours: int = 0, minutes: int = 0, seconds: int = 0) -> int:
    """Return the timestamp after delta time."""
    return current_utc_timestamp() + hours * 3600 + minutes * 60 + seconds


def timestamp_to_hex(timestamp: float | int) -> str:
    """Convert timestamp (in seconds) to Hexadecimal string"""
    return uuid7(int(timestamp)).hex[:8]


def uuid7_to_timestamp(uuid: str) -> int:
    """Convert uuid7 string to timestamp"""
    return UUID(uuid).timestamp
