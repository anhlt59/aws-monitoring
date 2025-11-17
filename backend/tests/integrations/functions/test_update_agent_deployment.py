from unittest.mock import MagicMock

import pytest

from src.common.exceptions import NotFoundError
from src.entrypoints.functions.update_deployment.main import handler, notifier
from tests.conftest import TEST_DIR
from tests.mock import load_event


def test_normal_case(agent_repo):
    # Agent
    event = load_event(TEST_DIR / "data" / "cloudformation_event.json")
    notifier.client.send = MagicMock(side_effect=lambda *a, **kw: None)
    handler(event, None)
    agent = agent_repo.get("000000000000")
    assert agent.status == "CREATE_COMPLETE"

    event.detail["status-details"]["status"] = "UPDATE_FAILED"
    notifier.client.send = MagicMock(side_effect=lambda *a, **kw: None)
    handler(event, None)
    agent = agent_repo.get("000000000000")
    assert agent.status == "UPDATE_FAILED"

    event.detail["status-details"]["status"] = "DELETE_COMPLETE"
    notifier.client.send = MagicMock(side_effect=lambda *a, **kw: None)
    handler(event, None)
    agent = agent_repo.get("000000000000")
    assert agent.status == "DELETE_COMPLETE"


def test_abnormal_case(agent_repo):
    """Test that non-CloudFormation events are rejected."""
    event = load_event(TEST_DIR / "data" / "health_event.json")

    # Handler should raise ValueError for non-CloudFormation events
    with pytest.raises(ValueError, match="Event is not a valid CloudFormation stack event"):
        handler(event, None)

    # No agent should be created
    with pytest.raises(NotFoundError):
        agent_repo.get("000000000000")
