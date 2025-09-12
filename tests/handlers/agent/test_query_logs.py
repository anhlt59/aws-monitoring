import json
import time
from uuid import uuid4

import boto3

from src.common.constants import AWS_ENDPOINT, AWS_REGION
from src.modules.agent.handlers.query_error_logs.main import handler


def mock_ecs_service():
    from src.infras.aws import ECSService

    class ECSMockService(ECSService):
        def list_clusters(self, **kwargs):
            return []

    # container.ecs_service.override(providers.Singleton(ECSMockService))


def mock_cloudwatch_logs(log_group_name: str):
    # Setup client
    client = boto3.client("logs", region_name=AWS_REGION, endpoint_url=AWS_ENDPOINT)
    log_stream_name = f"2025/01/01/[$LATEST]{uuid4()}"

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
    timestamp = int(time.time() * 1000 - 1000 * 60 * 5)  # 5 minutes ago

    log_events = [
        # Successful invocation
        {"timestamp": timestamp, "message": f"START RequestId: {request_id_1} Version: $LATEST"},
        {"timestamp": timestamp + 10, "message": json.dumps({"event": "user.login", "status": "success"})},
        {"timestamp": timestamp + 20, "message": f"END RequestId: {request_id_1}"},
        {
            "timestamp": timestamp + 30,
            "message": f"REPORT RequestId: {request_id_1} Duration: 5.32 ms  Memory Size: 128 MB  Max Memory Used: 34 MB",
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
            "message": f"REPORT RequestId: {request_id_2} Duration: 7.12 ms  Memory Size: 128 MB  Max Memory Used: 40 MB",
        },
    ]
    # Send log events
    client.put_log_events(logGroupName=log_group_name, logStreamName=log_stream_name, logEvents=log_events)
    print("✅ Fake success and error logs sent to CloudWatch (LocalStack).")


def test_query_logs():
    log_group_name = "/aws/lambda/monitoring-master-local-HandleMonitoringEvents"
    mock_cloudwatch_logs(log_group_name)
    handler(None, None)
