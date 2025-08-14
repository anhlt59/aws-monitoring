import os

from src.adapters.aws.data_classes import (
    CwAlarmEvent,
    EventBridgeEvent,
    GuardDutyFindingEvent,
    HealthEvent,
    event_source,
)
from src.adapters.db import EventRepository
from src.adapters.notifiers import SlackNotifier
from src.common.logger import logger
from src.common.utils.datetime_utils import datetime_str_to_timestamp
from src.models import Event

from .messages import (
    render_agent_err_log_message,
    render_cw_alarm_message,
    render_guardduty_message,
    render_health_message,
)

CW_ALARM_TEMPLATE_FILE = "slack_messages/cloudwatch_alarm.json"
CW_LOG_TEMPLATE_FILE = "slack_messages/cloudwatch_log.json"
GUARDDUTY_TEMPLATE_FILE = "slack_messages/guardduty.json"
HEALTH_TEMPLATE_FILE = "slack_messages/health.json"

repo = EventRepository()
notifier = SlackNotifier(os.environ.get("MONITORING_WEBHOOK_URL"))


def create_event(event: EventBridgeEvent):
    """Store the event in the database."""
    model = Event(
        id=event.get_id,
        account=event.account,
        region=event.region,
        source=event.source,
        detail=event.detail,
        detail_type=event.detail_type,
        resources=event.resources,
        published_at=datetime_str_to_timestamp(event.time),
    )

    try:
        repo.create(model)
        logger.info(f"Event<{model.id}> inserted")
    except Exception as e:
        logger.debug(model.model_dump())
        logger.error(f"Failed to insert event: {e}")
        raise e


def push_notification(event: EventBridgeEvent):
    """Push notification based on the event source."""
    match event.source:
        case "aws.health" | "monitoring.agent.health":
            message = render_health_message(HealthEvent(event))
        case "aws.guardduty" | "monitoring.agent.guardduty":
            message = render_guardduty_message(GuardDutyFindingEvent(event))
        case "aws.cloudwatch" | "monitoring.agent.cloudwatch":
            message = render_cw_alarm_message(CwAlarmEvent(event))
        case "monitoring.agent.logs":
            message = render_agent_err_log_message(event)
        case _:
            logger.warning(f"Event<{event.get_id}>: Unknown event source '{event.source}'")
            raise ValueError(f"Unknown event source: {event.source}")
    notifier.notify(message)
    logger.info(f"Sent Event<{event.get_id}> notification")


# @logger.inject_lambda_context(log_event=True)
@event_source(data_class=EventBridgeEvent)
def handler(event: EventBridgeEvent, context):
    """Handle the incoming event."""
    logger.debug(event.raw_event)
    create_event(event)
    push_notification(event)
