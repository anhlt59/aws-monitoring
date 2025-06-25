from src.handlers.master.api.events import handler


def test_get_event():
    event_id = "test_event_id"
    response = handler.get_event(event_id)
    assert response["id"] == event_id, f"Expected event ID {event_id}, got {response['id']}"
