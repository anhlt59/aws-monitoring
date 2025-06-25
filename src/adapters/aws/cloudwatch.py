from datetime import datetime
from typing import Iterable

import boto3
from types_boto3_logs.client import CloudWatchLogsClient
from types_boto3_logs.type_defs import OutputLogEventTypeDef

from src.common.logger import logger
from src.common.meta import SingletonMeta


class CloudwatchLogService(metaclass=SingletonMeta):
    client: CloudWatchLogsClient

    def __init__(self):
        self.client = boto3.client("logs")

    def query_logs(
        self, log_groups: str, query: str, start_time: datetime, end_time: datetime
    ) -> Iterable[OutputLogEventTypeDef]:
        params = {
            "logGroupNames": log_groups,
            "queryString": query,
            "startTime": int(start_time.timestamp() * 1000),
            "endTime": int(end_time.timestamp() * 1000),
            "startFromHead": True,
        }
        while True:
            response = self.client.get_log_events(**params)
            yield from response.get("events", [])

            if next_token := response.get("nextForwardToken"):
                params["nextToken"] = next_token
                logger.debug(f"Next token {next_token}")
            else:
                break
