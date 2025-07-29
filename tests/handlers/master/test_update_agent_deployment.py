from mock import MagicMock

from src.handlers.master.update_agent_deployment.main import handler, notifier


def test_normal_case(agent_repo):
    event = {
        "version": "0",
        "id": "ccde5842-a0b2-c911-5f5f-cdf8417f995d",
        "detail-type": "CloudFormation Stack Status Change",
        "source": "aws.cloudformation",
        "account": "000000000000",
        "time": "2025-07-28T15:37:34Z",
        "region": "us-east-1",
        "resources": [],
        "detail": {
            "stack-id": "arn:aws:cloudformation:ap-northeast-1:000000000000:stack/monitoring-agent-local/99c87d30-690d-11f0-bd3a-0a7c3e4bb8a7",
            "status-details": {"status": "CREATE_COMPLETE", "detailed-status": "", "status-reason": ""},
        },
    }
    notifier.notify = MagicMock(side_effect=lambda *a, **kw: None)
    handler(event, None)

    account = agent_repo.get("000000000000")
    assert account.id == "000000000000"
    assert account.region == "us-east-1"
    assert account.status == "CREATE_COMPLETE"
