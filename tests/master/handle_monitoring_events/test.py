from src.handlers.master.handle_monitoring_events.main import handler
from tests.conftest import TEST_DIR
from tests.mock import load_events, mock_lambda_context, truncate_event_table

EVENT_DIR = TEST_DIR / "master" / "handle_monitoring_events" / "events"


def test_handle_monitoring_events():
    truncate_event_table()
    # for event in load_events(EVENT_DIR):
    for event in load_events(file_path=EVENT_DIR / "guardduty_event.json"):
        response = handler(event, mock_lambda_context("handle_monitoring_events"))
        print(response)
