from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent

from src.common.logger import logger
from src.common.utils.datetime_utils import datetime_str_to_timestamp
from src.domain.models import Event
from src.domain.ports.notifier import IEventNotifier
from src.domain.ports.repositories import IEventRepository


def insert_monitoring_event_use_case(event: EventBridgeEvent, event_repo: IEventRepository, notifier: IEventNotifier):
    """Insert monitoring event use-case.
    1. Insert the event into the database.
    2. Notify the event to the subscribers.
    """
    # 1. Insert the event into the database
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
    event_repo.create(model)
    logger.info(f"Event<{model.id}> inserted")

    # 2. Notify the event via the notifier
    notifier.notify(event)
    logger.info(f"Sent Event<{model.id}> successfully")
