import os

from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent, event_source

from src.adapters.db.repositories import EventRepository
from src.adapters.notifiers import SlackNotifier
from src.common.logger import logger
from src.models import Event

from .push_notifiactions import push_alarm_notification, push_error_log_notification, push_health_notification

repo = EventRepository()
notifier = SlackNotifier(os.environ.get("WEBHOOK_URL"))


@logger.inject_lambda_context(log_event=True)
@event_source(data_class=EventBridgeEvent)
def handler(event: EventBridgeEvent, context):
    model = Event(
        id=event.get_id,
        account=event.account,
        source=event.source,
        detail=event.detail,
        created_at=int(event.time),
        updated_at=int(event.time),
    )
    # Store the event in the database
    repo.create(model)
    logger.info(f"Event<{model.id}> created")

    # Push notification to Slack
    match model.source:
        case "aws.health":
            push_health_notification(event, notifier)
        case "aws.logs":
            push_error_log_notification(event, notifier)
        case "aws.alarm":
            push_alarm_notification(event, notifier)
