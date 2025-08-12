from datetime import UTC, datetime, timezone


def current_utc_timestamp() -> int:
    return round(datetime.now(UTC).timestamp())


def datetime_str_to_timestamp(dt_str: str, dt_format="%Y-%m-%dT%H:%M:%SZ") -> int:
    """Convert ISO 8601 UTC string (e.g., '2023-08-29T03:13:27Z') to Unix timestamp (int)."""
    return int(datetime.strptime(dt_str, dt_format).replace(tzinfo=timezone.utc).timestamp())


def round_n_minutes(dt: datetime, n: int = 5) -> datetime:
    """
    Rounds down to the nearest n-minute interval
    :param dt: The datetime object to be rounded.
    :param n: The interval size in minutes.
    :return: The rounded datetime
    """
    new_minute = (dt.minute // n) * n
    rounded_time = dt.replace(minute=new_minute, second=0, microsecond=0)
    return rounded_time
