import os
from datetime import datetime, timedelta

from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent, event_source

from src.adapters.db import EventRepository
from src.adapters.notifiers import SlackNotifier
from src.common.logger import logger
from src.models.monitoring_event import ListEventsDTO

repo = EventRepository()
notifier = SlackNotifier(os.environ.get("WEBHOOK_URL"))


# @logger.inject_lambda_context(log_event=True)
@event_source(data_class=EventBridgeEvent)
def handler(event: EventBridgeEvent, context):
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)

    # Fetch events from the repository
    events = repo.list(
        ListEventsDTO(
            start_date=int(start_date.timestamp()),
            end_date=int(end_date.timestamp()),
            limit=100,
        )
    )
    logger.debug(f"Fetched {len(events.items)} events for daily report")

    # Push notification to Slack
    # push_report_notification(event, notifier)
