import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from uuid import uuid4

import boto3
from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent

from src.adapters.db import EventRepository
from src.common.configs import AWS_ENDPOINT, AWS_REGION
from src.common.utils.files import list_files
from src.models.event import ListEventsDTO


@dataclass
class LambdaContext:
    aws_request_id: str
    function_name: str
    function_version: str
    invoked_function_arn: str
    memory_limit_in_mb: int
    log_group_name: str
    log_stream_name: str


def mock_lambda_context(function_name: str) -> LambdaContext:
    return LambdaContext(
        aws_request_id="1234567890abcdef",
        function_name=function_name,
        function_version="$LATEST",
        invoked_function_arn=f"arn:aws:lambda:us-east-1:123456789012:function:{function_name}",
        memory_limit_in_mb=128,
        log_group_name=f"/aws/lambda/{function_name}",
        log_stream_name="2023/08/29/[$LATEST]1234567890abcdef1234567890abcdef",
    )


def get_rest_api_endpoint(api_name: str, region="us-east-1", endpoint="http://localhost:4566"):
    client = boto3.client("apigateway", region_name=region, endpoint_url=endpoint)
    # Find API ID by name
    apis = client.get_rest_apis()
    if api := next((a for a in apis["items"] if a["name"] == api_name), None):
        api_id = api["id"]
    else:
        raise Exception(f"REST API named '{api_name}' not found.")
    # Get the first stage
    stages = client.get_stages(restApiId=api_id)
    if not stages["item"]:
        raise Exception(f"No stages found for API ID {api_id}")
    stage_name = stages["item"][0]["stageName"]
    # Construct URL
    return f"http://{api_id}.execute-api.localhost.localstack.cloud:4566/{stage_name}"


def load_events(dir_path: Path = None, file_path: Path = None) -> Iterable[EventBridgeEvent]:
    files: list[Path] = []
    if dir_path is not None and dir_path.is_dir():
        files.extend(list(list_files(dir_path)))
    if file_path is not None and file_path.is_file():
        files.append(file_path)
    if len(files) == 0:
        raise Exception("No events found.")

    for file in files:
        with open(file) as f:
            data = json.load(f)
            yield EventBridgeEvent(data)


def truncate_event_table():
    repo = EventRepository()
    dto = ListEventsDTO()
    for event in repo.list(dto).items:
        repo.delete(event.persistence_id)


def mock_cloudwatch_logs(log_group_name: str = "/aws/lambda/test-function"):
    # Setup client
    client = boto3.client("logs", region_name=AWS_REGION, endpoint_url=AWS_ENDPOINT)
    log_stream_name = f"2025/06/21/[$LATEST]{uuid4()}"

    # Create log group & log stream
    try:
        client.create_log_group(logGroupName=log_group_name)
    except client.exceptions.ResourceAlreadyExistsException:
        pass
    try:
        client.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)
    except client.exceptions.ResourceAlreadyExistsException:
        pass

    # Generate fake logs
    request_id_1 = str(uuid4())
    request_id_2 = str(uuid4())
    timestamp = int(time.time() * 1000 - 1000 * 60 * 60 * 12)  # 12 hours ago

    log_events = [
        # Successful invocation
        {"timestamp": timestamp, "message": f"START RequestId: {request_id_1} Version: $LATEST"},
        {"timestamp": timestamp + 10, "message": json.dumps({"event": "user.login", "status": "success"})},
        {"timestamp": timestamp + 20, "message": f"END RequestId: {request_id_1}"},
        {
            "timestamp": timestamp + 30,
            "message": f"REPORT RequestId: {request_id_1}  Duration: 5.32 ms  Memory Size: 128 MB  Max Memory Used: 34 MB",
        },
        # Failed invocation
        {"timestamp": timestamp + 100, "message": f"START RequestId: {request_id_2} Version: $LATEST"},
        {
            "timestamp": timestamp + 110,
            "message": json.dumps({"event": "user.login", "status": "error", "reason": "Invalid credentials"}),
        },
        {"timestamp": timestamp + 120, "message": "Traceback (most recent call last):"},
        {"timestamp": timestamp + 130, "message": '  File "/var/task/lambda_function.py", line 10, in handler'},
        {"timestamp": timestamp + 140, "message": '    raise Exception("Authentication failed")'},
        {"timestamp": timestamp + 150, "message": "Exception: Authentication failed"},
        {"timestamp": timestamp + 160, "message": f"END RequestId: {request_id_2}"},
        {
            "timestamp": timestamp + 170,
            "message": f"REPORT RequestId: {request_id_2}  Duration: 7.12 ms  Memory Size: 128 MB  Max Memory Used: 40 MB",
        },
    ]
    # Send log events
    client.put_log_events(logGroupName=log_group_name, logStreamName=log_stream_name, logEvents=log_events)
    print("✅ Fake success and error logs sent to CloudWatch (LocalStack).")
