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
