from itertools import islice
from typing import Any, Iterable


def chunks(objs: Iterable[Any], limit: int) -> Iterable[list[Any]]:
    """
    Yield successive limit-sized chunks from a iterable.
    :param objs: list of any objects
    :param limit: chunk size
    :return: iterable limit-sized chunks
    """
    if isinstance(objs, list) or isinstance(objs, tuple):
        objs = iter(objs)
    while batch := list(islice(objs, limit)):
        yield batch
