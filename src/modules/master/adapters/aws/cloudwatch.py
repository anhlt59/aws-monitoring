import time
from collections import defaultdict
from datetime import datetime

import boto3
from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator
from types_boto3_logs.client import CloudWatchLogsClient

from src.libs.configs import AWS_ENDPOINT, AWS_REGION
from src.libs.logger import logger
from src.libs.meta import SingletonMeta


# Models ------------------------------------
class CwQueryParam(BaseModel):
    log_group_names: list[str]
    query_string: str
    start_time: int
    end_time: int
    timeout: int = 15
    delay: int = 1
    model_config = ConfigDict(validate_assignment=True, str_strip_whitespace=True)

    @field_validator("query_string", mode="after")
    @classmethod
    def validate_query_string(cls, value: str, info) -> str:
        if not value:
            raise ValueError("Query string cannot be empty")
        if not value.startswith("fields"):
            raise ValueError("Invalid query string format")
        if "@log" not in value or "@message" not in value:
            raise ValueError("Query string must include '@log' and '@message' fields")
        if "@logStream" not in value:
            logger.warning("Query string should include '@logStream' for better results")
        return value

    @field_validator("end_time", mode="after")
    @classmethod
    def validate_end_time(cls, value: datetime, info: ValidationInfo) -> datetime:
        start_time = info.data.get("start_time")
        if start_time and value < start_time:
            raise ValueError("End time must be greater than or equal to start time")
        return value


class CwLog(BaseModel):
    timestamp: int | None = None
    message: str
    log: str
    log_stream: str | None = None
    model_config = ConfigDict(extra="ignore")


class CwQueryResult(BaseModel):
    log_group_name: str
    logs: list[CwLog] = []


# Service -----------------------------------
class CloudwatchLogService(metaclass=SingletonMeta):
    client: CloudWatchLogsClient

    def __init__(self):
        self.client = boto3.client("logs", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION)

    def query_logs(self, param: CwQueryParam) -> list[CwQueryResult]:
        logger.debug(f"Querying logs for groups: {param.log_group_names} from {param.start_time} to {param.end_time}")
        query_time = time.time()
        # start the query
        start_query_response = self.client.start_query(
            logGroupNames=param.log_group_names,
            queryString=param.query_string,
            startTime=param.start_time,
            endTime=param.end_time,
        )
        query_id = start_query_response.get("queryId")

        # Wait for the query to complete
        response = {"status": "Running"}
        while response.get("status") == "Running":
            if time.time() - query_time > param.timeout:
                raise Exception("Query timed out")
            time.sleep(param.delay)
            response = self.client.get_query_results(queryId=query_id)
        logger.debug(f"Query completed with status: {response.get('status')}")

        # categorize results by log_group_name
        categorized_results = defaultdict(list)
        for result in response.get("results", []):
            cw_log = CwLog.model_validate({item.get("field", " ")[1:]: item.get("value") for item in result})
            categorized_results[cw_log.log].append(cw_log)

        return [CwQueryResult(log_group_name=name, logs=logs) for name, logs in categorized_results.items()]
