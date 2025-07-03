from datetime import datetime, timedelta

from src.adapters.aws.cloudwatch import CloudwatchLogService, CwQueryParam
from tests.mock import mock_cloudwatch_logs


def test_query_logs():
    log_group_name = "/aws/lambda/test-function"
    mock_cloudwatch_logs(log_group_name)
    start_time = datetime.now() - timedelta(days=1)
    end_time = datetime.now()

    dto = CwQueryParam(
        logGroupNames=[log_group_name],
        queryString="fields @timestamp, @log, @message | sort @timestamp desc | limit 20",
        startTime=int(start_time.timestamp()),
        endTime=int(end_time.timestamp()),
    )

    service = CloudwatchLogService()
    results = list(service.query_logs(dto))

    assert isinstance(results, list)
    assert len(results) > 0
