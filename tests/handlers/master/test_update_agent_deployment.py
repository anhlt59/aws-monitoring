from mock import MagicMock

from src.handlers.master.update_agent_deployment.main import handler, notifier
from tests.conftest import TEST_DIR
from tests.mock import load_event


def test_normal_case(agent_repo):
    event = load_event(TEST_DIR / "data" / "cloudformation_event.json")
    notifier.notify = MagicMock(side_effect=lambda *a, **kw: None)
    handler(event, None)

    account = agent_repo.get("000000000000")
    assert account.id == "000000000000"
    assert account.region == "us-east-1"
    assert account.status == "CREATE_COMPLETE"
