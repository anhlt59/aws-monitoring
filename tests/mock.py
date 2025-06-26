import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import boto3
from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent

from src.adapters.db import EventRepository
from src.common.utils.files import list_files
from src.models.monitoring_event import ListEventsDTO


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
