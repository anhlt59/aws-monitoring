from src.common.logger import logger
from src.common.utils.datetime_utils import datetime_str_to_timestamp
from src.infras.aws.data_classes import EventBridgeEvent, event_source
from src.modules.master.configs import MONITORING_WEBHOOK_URL
from src.modules.master.models import Event
from src.modules.master.services.notifiers import (
    CWAlarmNotifier,
    CWLogNotifier,
    GuardDutyNotifier,
    HealthNotifier,
    SlackClient,
)
from src.modules.master.services.repositories import EventRepository

# Initialize services
event_repo = EventRepository()
slack_client = SlackClient(MONITORING_WEBHOOK_URL)


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
        event_repo.create(model)
        logger.info(f"Event<{model.id}> inserted")
    except Exception as e:
        logger.debug(model.model_dump())
        logger.error(f"Failed to insert event: {e}")
        raise e


def push_notification(event: EventBridgeEvent):
    """Push notification based on the event source."""
    match event.source:
        case "aws.health" | "monitoring.agent.health":
            notifier = HealthNotifier(slack_client)
        case "aws.guardduty" | "monitoring.agent.guardduty":
            notifier = GuardDutyNotifier(slack_client)
        case "aws.cloudwatch" | "monitoring.agent.cloudwatch":
            notifier = CWAlarmNotifier(slack_client)
        case "monitoring.agent.logs":
            notifier = CWLogNotifier(slack_client)
        case _:
            logger.warning(f"Event<{event.get_id}>: Unknown event source '{event.source}'")
            raise ValueError(f"Unknown event source: {event.source}")
    notifier.notify(event)
    logger.info(f"Sent Event<{event.get_id}> successfully")


# @logger.inject_lambda_context(log_event=True)
@event_source(data_class=EventBridgeEvent)
def handler(event: EventBridgeEvent, context):
    """Handle the incoming event."""
    logger.debug(event.raw_event)
    create_event(event)
    push_notification(event)
