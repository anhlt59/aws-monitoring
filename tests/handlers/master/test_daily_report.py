import time
from unittest.mock import Mock
from uuid import uuid4

from src.modules.master.handlers.daily_report.main import handler, notifier
from src.modules.master.models import Event
from src.modules.master.services.repositories import EventRepository


def test_normal_case(event_repo: EventRepository):
    # Create dummy events
    now = int(time.time())
    for i in range(5):
        event = Event(
            id=f"{now}-{uuid4()}",
            account="000000000000",
            region="us-east-1",
            source="agent.test",
            detail={"message": f"Test event {i}"},
            detail_type="TestEvent",
            resources=[],
            published_at=now - 86400 - i * 60,
            updated_at=now - 86400 - i * 60,
        )
        event_repo.create(event)

    # Mock the notifier's report method
    notifier.report = Mock()

    # Invoke the handler
    handler(None, None)

    notifier.report.assert_called_once()
