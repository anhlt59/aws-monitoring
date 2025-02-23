import re
from datetime import datetime
from itertools import islice
from typing import Any, Iterable

topic_compiler = re.compile(r"^/\w+/(.+)/\w+")


def get_imei_from_topic(topic_name: str) -> str | None:
    """Extract `imei` from topic name"""
    if reg := topic_compiler.search(topic_name):
        return reg.group(1)


def chunks(objs: Iterable[Any], limit: int) -> Iterable[list[Any]]:
    """
    Yield successive limit-sized chunks from a iterable.
    :param objs: list of any objects
    :param limit: chunk size
    :return: iterable limit-sized chunks
    """
    objs = iter(objs)
    while batch := list(islice(objs, limit)):
        yield batch


def round_n_minutes(dt: datetime, n: int = 30):
    """
    Rounds down to the nearest n-minute interval
    :param dt: The datetime object to be rounded.
    :param n: The interval size in minutes.
    :return: The rounded datetime
    """
    new_minute = (dt.minute // n) * n
    rounded_time = dt.replace(minute=new_minute, second=0, microsecond=0)
    return rounded_time


def parse_version(version: str) -> int:
    """
    Parse version string into tuple of integers
    1.1.1 -> 1001001
    :param version: version string
    :return: int
    """
    parsed_int = tuple(map(int, version.split(".")))
    return sum(num * 1000**i for i, num in enumerate(reversed(parsed_int)))
