import time
from collections import defaultdict

import boto3
from pydantic import BaseModel
from types_boto3_logs.client import CloudWatchLogsClient
from types_boto3_logs.type_defs import ResultFieldTypeDef

from src.common.constants import AWS_ENDPOINT, AWS_REGION
from src.common.logger import logger
from src.common.meta import SingletonMeta


class CwLog(BaseModel):
    timestamp: int | None = None
    message: str
    log: str
    log_stream: str | None = None


class CwQueryResult(BaseModel):
    log_group_name: str
    logs: list[CwLog] = []


class CloudwatchLogService(metaclass=SingletonMeta):
    client: CloudWatchLogsClient

    def __init__(self, region=AWS_REGION, endpoint_url=AWS_ENDPOINT):
        self.client = boto3.client("logs", region_name=region, endpoint_url=endpoint_url)

    def query_logs(
        self,
        log_group_names: list[str],
        query_string: str,
        start_time: int,
        end_time: int,
        timeout: int = 15,
        delay: int = 1,
    ) -> list[ResultFieldTypeDef]:
        logger.debug(f"Querying logs for groups: {log_group_names} from {start_time} to {end_time}")
        query_time = time.time()
        # start the query
        start_query_response = self.client.start_query(
            logGroupNames=log_group_names,
            queryString=query_string,
            startTime=start_time,
            endTime=end_time,
        )
        query_id = start_query_response.get("queryId")

        # Wait for the query to complete
        response = {"status": "Running"}
        while response.get("status") == "Running":
            if time.time() - query_time > timeout:
                raise Exception("Query timed out")
            time.sleep(delay)
            response = self.client.get_query_results(queryId=query_id)
        results = response.get("results", [])
        logger.debug(f"Query completed with status: {response.get('status')}")

        # categorize results by log_group_name
        categorized_results = defaultdict(list)
        for result in results:
            cw_log = CwLog.model_validate({item.get("field", " ")[1:]: item.get("value") for item in result})
            categorized_results[cw_log.log].append(cw_log)

        yield from (CwQueryResult(log_group_name=name, logs=logs) for name, logs in categorized_results.items())
