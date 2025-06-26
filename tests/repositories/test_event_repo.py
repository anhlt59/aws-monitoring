def test_get_event(dummy_event, event_repo):
    retrieved = event_repo.get(dummy_event.persistence_id)
    assert retrieved.id == dummy_event.id
    assert retrieved.account == dummy_event.account
    assert retrieved.source == dummy_event.source
