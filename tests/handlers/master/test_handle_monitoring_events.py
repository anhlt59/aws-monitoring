from mock import MagicMock

from src.modules.master.handlers.handle_monitoring_events.main import handler, slack_client
from tests.conftest import TEST_DIR
from tests.mock import load_event


def test_handle_health_event(event_repo):
    health_event = load_event(TEST_DIR / "data" / "health_event.json")
    slack_client.send = MagicMock(side_effect=lambda *a, **kw: None)
    handler(health_event, None)

    event = event_repo.get("1735689600-00000000-0000-0000-0000-000000000000")
    assert event is not None
    assert event.account == "000000000000"
    assert event.region == "us-east-1"
    assert event.source == "aws.health"
    assert event.detail_type == "AWS Health Event"


def test_handle_guardduty_event(event_repo):
    guardduty_event = load_event(TEST_DIR / "data" / "guardduty_event.json")
    slack_client.send = MagicMock(side_effect=lambda *a, **kw: None)
    handler(guardduty_event, None)

    event = event_repo.get("1735689600-00000000-0000-0000-0000-000000000000")
    assert event is not None
    assert event.account == "000000000000"
    assert event.region == "us-east-1"
    assert event.source == "aws.guardduty"
    assert event.detail_type == "GuardDuty Finding"


def test_handle_alarm_event(event_repo):
    alarm_event = load_event(TEST_DIR / "data" / "alarm_event.json")
    slack_client.send = MagicMock(side_effect=lambda *a, **kw: None)
    handler(alarm_event, None)

    event = event_repo.get("1735689600-00000000-0000-0000-0000-000000000000")
    assert event is not None
    assert event.account == "000000000000"
    assert event.region == "us-east-1"
    assert event.source == "aws.cloudwatch"
    assert event.detail_type == "CloudWatch Alarm State Change"


def test_handle_cwlog_event(event_repo):
    cwlog_event = load_event(TEST_DIR / "data" / "logs_event.json")
    # slack_client.send = MagicMock(side_effect=lambda *a, **kw: None)
    handler(cwlog_event, None)

    event = event_repo.get("1735689600-00000000-0000-0000-0000-000000000000")
    assert event is not None
    assert event.account == "000000000000"
    assert event.region == "us-east-1"
    assert event.source == "aws.cloudwatch"
    assert event.detail_type == "CloudWatch Alarm State Change"
