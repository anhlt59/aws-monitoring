import pytest

from src.common.exceptions.http import NotFoundError
from src.models import Event


def test_create_event(event_repo):
    event = Event(
        id="123456789012",
        account="000000000000",
        source="test-source",
        detail={"key": "value"},
    )
    event_repo.create(event)
    retrieved_event = event_repo.get(event.persistence_id)
    assert retrieved_event.id == event.id
    assert retrieved_event.account == event.account
    assert retrieved_event.source == event.source
    assert retrieved_event.detail == event.detail


def test_delete_event(event_repo, dummy_event):
    event_repo.delete(dummy_event.persistence_id)
    with pytest.raises(NotFoundError):
        event_repo.get(dummy_event.persistence_id)


def test_list_events(event_repo):
    events = []
    for i in range(5):
        event = Event(
            id=f"event-{i}",
            account="000000000000",
            source="test-source",
            detail={"key": f"value-{i}"},
        )
        event_repo.create(event)
        events.append(event)

    events = event_repo.list()
    assert len(events.items) == 5
