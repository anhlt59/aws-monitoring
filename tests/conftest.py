import sys
import time
from pathlib import Path

import pytest
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_DIR = BASE_DIR / "tests"
sys.path.append(str(BASE_DIR))
load_dotenv(BASE_DIR / ".env.local")

# fmt: off
from src.adapters.db import AccountRepository, EventRepository  # noqa
from src.models import Account, Event  # noqa
from src.models.event import ListEventsDTO  # noqa

# fmt: on


# fixtures -----
@pytest.fixture()
def event_repo():
    repo = EventRepository()
    yield repo
    # Cleanup
    for event in repo.list(ListEventsDTO()).items:
        repo.delete(event.id)


@pytest.fixture()
def account_repo():
    repo = AccountRepository()
    yield repo
    # Cleanup
    for event in repo.list().items:
        repo.delete(event.id)


@pytest.fixture
def dummy_event(event_repo):
    event = Event(
        id="111111111111",
        account="000000000000",
        source="test-source",
        detail={"key": "value"},
    )
    event_repo.create(event)
    yield event


@pytest.fixture
def dummy_account(account_repo):
    now = int(time.time())
    account = Account(
        id="000000000000",
        name="Test Account",
        stage="test",
        region="us-west-2",
        deployed_at=now,
        created_at=now,
    )
    account_repo.create(account)
    yield account
