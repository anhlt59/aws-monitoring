from src.handlers.master.handle_monitoring_events.main import handler
from tests.conftest import TEST_DIR
from tests.mock import load_events, mock_lambda_context, truncate_event_table


def test_handle_monitoring_events():
    truncate_event_table()
    for event in load_events(TEST_DIR / "data"):
        response = handler(event, mock_lambda_context("handle_monitoring_events"))
        print(response)
