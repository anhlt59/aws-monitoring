import time

import boto3
from pydantic import BaseModel, ConfigDict
from types_boto3_logs.client import CloudWatchLogsClient, StartQueryRequestTypeDef

from src.common.configs import AWS_ENDPOINT, AWS_REGION
from src.common.logger import logger
from src.common.meta import SingletonMeta


class InsightLog(BaseModel):
    timestamp: int | None = None
    message: str
    log: str | None = None
    logStream: str | None = None
    model_config = ConfigDict(extra="ignore")


class CloudwatchLogService(metaclass=SingletonMeta):
    client: CloudWatchLogsClient

    def __init__(self):
        self.client = boto3.client("logs", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION)

    def query_logs(self, param: StartQueryRequestTypeDef, timeout=15, delay=1) -> list[InsightLog]:
        logger.debug(f"Querying logs for groups: {param.logGroupNames} from {param.startTime} to {param.endTime}")
        query_time = time.time()
        start_query_response = self.client.start_query(
            logGroupNames=param.logGroupNames,
            queryString=param.queryString,
            startTime=int(param.startTime.timestamp()),
            endTime=int(param.endTime.timestamp()),
        )
        query_id = start_query_response.get("queryId")
        response = {"status": "Running"}
        # Wait for the query to complete
        while response.get("status") == "Running":
            if time.time() - query_time > timeout:
                raise Exception("Query timed out")
            time.sleep(delay)
            response = self.client.get_query_results(queryId=query_id)

        logger.debug(f"Query completed with status: {response.get('status')}")
        return [
            InsightLog.model_validate({item.get("field", " ")[1:]: item.get("value") for item in result})
            for result in response.get("results", [])
        ]
