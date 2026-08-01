import pytest

from src.common.exceptions import NotFoundError
from src.domain.models import Event


def test_create_event(event_repo):
    event = Event(
        id="123456789012",
        account="000000000000",
        region="us-east-1",
        source="monitoring.test",
        detail={"key": "value"},
        detail_type="test-detail-type",
    )
    event_repo.create(event)
    retrieved_event = event_repo.get(event.id)
    assert retrieved_event.id == event.id
    assert retrieved_event.account == event.account
    assert retrieved_event.source == event.source
    assert retrieved_event.detail == event.detail


def test_delete_event(event_repo, dummy_event):
    event_repo.delete(dummy_event.id)
    with pytest.raises(NotFoundError):
        event_repo.get(dummy_event.id)


def test_list_events(event_repo):
    events = []
    for i in range(5):
        event = Event(
            id=f"event-{i}",
            account="000000000000",
            region="us-east-1",
            source="monitoring.test",
            detail={"key": f"value-{i}"},
            detail_type="test-detail-type",
        )
        event_repo.create(event)
        events.append(event)

    events = event_repo.all()
    assert len(events.items) == 5
