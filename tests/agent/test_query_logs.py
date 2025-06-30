from datetime import datetime, timedelta

from src.adapters.aws.cloudwatch import CloudwatchLogService, InsightQuery
from tests.mock import mock_cloudwatch_logs


def test_query_logs():
    log_group_name = "/aws/lambda/test-function"
    mock_cloudwatch_logs(log_group_name)
    start_time = datetime.now() - timedelta(days=1)
    end_time = datetime.now()

    dto = InsightQuery(
        logGroupNames=[log_group_name],
        queryString="fields @timestamp, @message | sort @timestamp desc | limit 20",
        startTime=start_time,
        endTime=end_time,
    )

    service = CloudwatchLogService()
    results = list(service.query_logs(dto))

    assert isinstance(results, list)
    assert len(results) > 0
