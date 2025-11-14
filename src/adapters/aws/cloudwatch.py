import asyncio

import aioboto3
from types_aioboto3_logs.client import CloudWatchLogsClient
from types_boto3_logs.type_defs import ResultFieldTypeDef

from src.common.constants import AWS_ENDPOINT, AWS_REGION
from src.common.exceptions import RequestTimeoutError
from src.common.logger import logger
from src.common.meta import SingletonMeta


class CloudwatchLogService(metaclass=SingletonMeta):
    def __init__(self, region=AWS_REGION, endpoint_url=AWS_ENDPOINT):
        self.region = region
        self.endpoint_url = endpoint_url
        self.session = aioboto3.Session()

    async def query_logs(
        self,
        log_group_names: list[str],
        query_string: str,
        start_time: int,
        end_time: int,
        timeout: int = 15,
        delay: int = 1,
    ) -> list[ResultFieldTypeDef]:
        logger.debug(f"Querying logs for groups: {log_group_names} from {start_time} to {end_time}")

        async with self.session.client("logs", region_name=self.region, endpoint_url=self.endpoint_url) as client:
            start_time_stamp = asyncio.get_event_loop().time()

            # start the query
            start_query_response = await client.start_query(
                logGroupNames=log_group_names,
                queryString=query_string,
                startTime=start_time,
                endTime=end_time,
            )
            query_id = start_query_response.get("queryId")

            # Wait for the query to complete
            response = {"status": "Running"}
            while response.get("status") == "Running":
                if asyncio.get_event_loop().time() - start_time_stamp > timeout:
                    raise RequestTimeoutError(
                        f"CloudWatch Logs Insights query timed out after {timeout}s for log groups: {log_group_names}"
                    )
                await asyncio.sleep(delay)
                response = await client.get_query_results(queryId=query_id)

            logger.debug(f"Query completed with status: {response.get('status')}")
            return response.get("results", [])
