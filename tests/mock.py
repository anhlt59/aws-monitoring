import json
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import boto3
from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent

from src.modules.master.models.event import ListEventsDTO
from src.modules.master.services.repositories import EventRepository


@dataclass
class LambdaContext:
    log_group_name: str
    log_stream_name: str
    function_name: str
    invoked_function_arn: str
    aws_request_id: str = "1234567890abcdef"
    memory_limit_in_mb: int = 128
    function_version: str = "$LATEST"


def mock_lambda_context(function_name: str) -> LambdaContext:
    return LambdaContext(
        function_name=function_name,
        invoked_function_arn=f"arn:aws:lambda:us-east-1:000000000000:function:{function_name}",
        log_group_name=f"/aws/lambda/{function_name}",
        log_stream_name="2025/01/01/[$LATEST]1234567890abcdef1234567890abcdef",
    )


def mock_api_gateway_event(method: str, path: str, params: dict | None = None, body: dict | None = None) -> dict:
    if params is not None:
        for key, value in params.items():
            params[key] = str(value)
    if body is not None:
        for key, value in body.items():
            body[key] = str(value)
    return {
        "headers": {"Accept": "*/*", "Host": "localhost:3000"},
        "queryStringParameters": params,
        "path": path,
        "body": body,
        "httpMethod": method,
        "isBase64Encoded": False,
        # 'multiValueQueryStringParameters': params,
        "pathParameters": None,
        "requestContext": {
            "accountId": "offlineContext_accountId",
            "apiId": "offlineContext_apiId",
            "domainName": "offlineContext_domainName",
            "domainPrefix": "offlineContext_domainPrefix",
            "extendedRequestId": "b246ada4-feed-4166-84ea-561af5f9d12e",
            "httpMethod": "GET",
            "identity": {
                "accessKey": None,
                "accountId": "offlineContext_accountId",
                "apiKey": "offlineContext_apiKey",
                "apiKeyId": "offlineContext_apiKeyId",
            },
            "path": path,
            "protocol": "HTTP/1.1",
            "requestId": str(uuid4()),
            "requestTime": "01/Aug/2025:12:16:53 +0700",
            "requestTimeEpoch": 1754111813121,
            "resourceId": "offlineContext_resourceId",
            "resourcePath": f"/local{path}",
            "stage": "local",
        },
        "resource": path.strip("/").split("/", 1)[0],  # Extract resource from path
        "stageVariables": None,
    }


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


def load_event(file: Path) -> EventBridgeEvent:
    if not file.exists():
        raise FileNotFoundError(f"Event file {file} does not exist.")

    with open(file) as f:
        data = json.load(f)

    return EventBridgeEvent(data)


def truncate_event_table():
    repo = EventRepository()
    dto = ListEventsDTO()
    for event in repo.list(dto).items:
        repo.delete(event.persistence_id)
