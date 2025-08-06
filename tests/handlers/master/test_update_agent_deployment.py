import pytest
from mock import MagicMock

from src.common.exceptions import NotFoundError
from src.handlers.master.update_agent_deployment.main import handler, notifier
from tests.conftest import TEST_DIR
from tests.mock import load_event


def test_normal_case(agent_repo):
    event = load_event(TEST_DIR / "data" / "cloudformation_event.json")
    notifier.notify = MagicMock(side_effect=lambda *a, **kw: None)
    handler(event, None)
    account = agent_repo.get("000000000000")
    assert account.status == "CREATE_COMPLETE"

    event.detail["status-details"]["status"] = "UPDATE_FAILED"
    notifier.notify = MagicMock(side_effect=lambda *a, **kw: None)
    handler(event, None)
    account = agent_repo.get("000000000000")
    assert account.status == "UPDATE_FAILED"

    event.detail["status-details"]["status"] = "DELETE_COMPLETE"
    notifier.notify = MagicMock(side_effect=lambda *a, **kw: None)
    handler(event, None)
    account = agent_repo.get("000000000000")
    assert account.status == "DELETE_COMPLETE"


def test_abnormal_case(agent_repo):
    event = load_event(TEST_DIR / "data" / "health_event.json")
    handler(event, None)

    with pytest.raises(NotFoundError):
        agent_repo.get("000000000000")
