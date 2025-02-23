#!/usr/local/bin/python3
import os
import time
from typing import List

import boto3

# boto3.setup_default_session(profile_name="default")

LOG_GROUPS = []
QUERY = """
fields @timestamp #, @message, @logStream, @log
| filter @message like /{}/
| sort @timestamp desc
| limit 20
"""

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

client = boto3.client("logs", region_name="ap-southeast-1")


def query_logs(
    query: str, log_groups: List[str], start_time: int, end_time: int, timeout: float = 15, delay: float = 1
):
    def _get_query_results():
        nonlocal query_id, timeout, delay

        response = client.get_query_results(queryId=query_id)
        if response["status"] == "Running":
            if timeout <= 0:
                raise Exception("Query timed out")
            # print("Waiting for query to complete ...")
            time.sleep(delay)
            return _get_query_results()
        return response.get("results")

    start_query_response = client.start_query(
        logGroupNames=log_groups,
        startTime=start_time,
        endTime=end_time,
        queryString=query,
    )
    if query_id := start_query_response.get("queryId"):
        return _get_query_results()


def main():
    pass


if __name__ == "__main__":
    main()
