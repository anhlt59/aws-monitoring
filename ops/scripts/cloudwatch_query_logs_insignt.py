#!/usr/local/bin/python3
import json
import os
import random
import time
from typing import List

import boto3
from dateutil.parser import parse

boto3.setup_default_session(profile_name="nbdb")

LOG_GROUPS = [
    "/aws/lambda/denaribots-dev-DummyIOTData",
    "/aws/lambda/denaribots-dev-DynamoDBStreamsToRDS",
]
QUERY = """
fields @timestamp #, @message, @logStream, @log
| filter @message like /{IMEI}/
| sort @timestamp desc
| limit 20
"""
START_TIME = "2023/11/03 03:15:00"
END_TIME = "2023/11/03 03:20:00"

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
with open(f"{BASE_DIR}/src/handlers/dummy/devices.json") as f:
    IMEIS = json.load(f)[:1000]
CHECKING_NUMBER = 100

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
    total = 0
    count = 0
    for _ in range(CHECKING_NUMBER):
        imei = random.choice(IMEIS)  # noqa
        logs = query_logs(
            QUERY.format(IMEI=imei),
            LOG_GROUPS,
            start_time=round(parse(START_TIME).timestamp()),
            end_time=round(parse(END_TIME).timestamp()),
        )

        if len(logs) >= 2:
            try:
                start_time = logs[-1][0]["value"]
                end_time = logs[0][0]["value"]
                duration = (parse(end_time) - parse(start_time)).total_seconds()
                print(f"{imei} - Duration - {duration}s")
                total += duration
                count += 1
            except Exception as e:
                print(f"{imei} - Error - {e}")
        else:
            print(f"{imei} - Warning - Not found")
    print(f"success: {count}, avg: {total / count}")


if __name__ == "__main__":
    main()
