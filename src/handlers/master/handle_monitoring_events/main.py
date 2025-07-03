import os

from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent, event_source

from src.adapters.db import EventRepository
from src.adapters.notifiers import SlackNotifier
from src.common.logger import logger
from src.common.utils.datetime_utils import datetime_str_to_timestamp
from src.models import Event

from .messages import create_alarm_message, create_guardduty_message, create_health_message, create_logs_message

repo = EventRepository()
notifier = SlackNotifier(os.environ.get("WEBHOOK_URL"))


def store_event(event: EventBridgeEvent):
    """Store the event in the database."""
    model = Event(
        id=event.get_id,
        account=event.account,
        source=event.source,
        detail=event.detail,
        published_at=datetime_str_to_timestamp(event.time),
    )
    repo.create(model)
    logger.info(f"Event<{model.id}> inserted")


def push_notification(event: EventBridgeEvent):
    """Push notification based on the event source."""
    match event.source:
        case "aws.health" | "monitoring.agent.health":
            message = create_health_message(event)
        case "aws.guardduty" | "monitoring.agent.guardduty":
            message = create_guardduty_message(event)
        case "aws.cloudwatch" | "monitoring.agent.alarm":
            message = create_alarm_message(event)
        case "monitoring.agent.logs":
            message = create_logs_message(event)
        case _:
            logger.warning(f"Event<{event.get_id}>: Unknown event source '{event.source}'")
            raise ValueError(f"Unknown event source: {event.source}")
    notifier.notify(message)
    logger.info(f"Sent Event<{event.get_id}> notification")


@logger.inject_lambda_context(log_event=True)
@event_source(data_class=EventBridgeEvent)
def handler(event: EventBridgeEvent, context):
    """Handle the incoming event."""
    store_event(event)
    push_notification(event)
