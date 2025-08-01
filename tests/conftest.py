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
from src.adapters.db import AgentRepository, EventRepository  # noqa
from src.models import Agent, Event  # noqa

# fmt: on


# fixtures -----
@pytest.fixture()
def event_repo():
    repo = EventRepository()
    yield repo
    # Cleanup
    for item in repo.list().items:
        repo.delete(item.persistence_id)


@pytest.fixture()
def agent_repo():
    repo = AgentRepository()
    yield repo
    # Cleanup
    for item in repo.list().items:
        repo.delete(item.persistence_id)


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
def dummy_agent(agent_repo):
    now = int(time.time())
    agent = Agent(
        id="000000000000",
        region="us-east-1",
        status="CREATE_COMPLETE",
        deployed_at=now,
        created_at=now,
    )
    agent_repo.create(agent)
    yield agent


if __name__ == "__main__":
    event_repo = EventRepository()
    for i in range(10):
        event = Event(
            id=f"event-{i}",
            account="000000000000",
            source="test-source",
            detail={"key": f"value-{i}"},
        )
        event_repo.create(event)
