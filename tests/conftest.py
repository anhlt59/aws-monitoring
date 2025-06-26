import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_DIR = BASE_DIR / "tests"
sys.path.append(str(BASE_DIR))
load_dotenv(BASE_DIR / ".env.local")

# fmt: off
from src.adapters.db.repositories.event import EventRepository  # noqa
from src.models import Event  # noqa
from src.models.monitoring_event import ListEventsDTO  # noqa

# fmt: on


# fixtures -----
@pytest.fixture()
def event_repo():
    repo = EventRepository()
    yield repo
    # Cleanup
    for event in repo.list(ListEventsDTO()).items:
        repo.delete(event.persistence_id)


@pytest.fixture
def dummy_event(event_repo):
    event = Event(
        id="111111111111",
        account="test-account",
        source="test-source",
        detail={"key": "value"},
    )
    event_repo.create(event)
    yield event
