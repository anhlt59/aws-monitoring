import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_DIR = BASE_DIR / "tests"
sys.path.append(str(BASE_DIR))
load_dotenv(BASE_DIR / ".env.local")

# fmt: off
from src.adapters.db.repositories import EventRepository, UserRepository  # noqa
from src.domain.models import Event  # noqa

# fmt: on


# fixtures -----
@pytest.fixture()
def event_repo():
    repo = EventRepository()
    yield repo
    # Cleanup
    for item in repo.all().items:
        repo.delete(item.id)


@pytest.fixture
def dummy_event(event_repo):
    event = Event(
        id="111111111111",
        account="000000000000",
        region="us-east-1",
        source="monitoring.test",
        detail={"key": "value"},
        detail_type="test-detail-type",
    )
    event_repo.create(event)
    yield event


@pytest.fixture()
def user_repo():
    repo = UserRepository()
    yield repo
    # Cleanup
    for item in repo.list().items:
        repo.delete(item.id)
