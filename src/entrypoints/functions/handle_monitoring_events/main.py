from src.adapters.aws.data_classes import EventBridgeEvent, event_source
from src.adapters.db.repositories import EventRepository
from src.adapters.notifiers import EventNotifier, SlackClient
from src.common.constants import MONITORING_WEBHOOK_URL
from src.common.logger import logger
from src.domain.use_cases.insert_monitoring_event import insert_monitoring_event_use_case

# Initialize services
event_repo = EventRepository()
notifier = EventNotifier(client=SlackClient(MONITORING_WEBHOOK_URL))


# @logger.inject_lambda_context(log_event=True)
@event_source(data_class=EventBridgeEvent)
def handler(event: EventBridgeEvent, context):
    logger.debug(event.raw_event)

    try:
        insert_monitoring_event_use_case(event, event_repo, notifier)
    except Exception as e:
        logger.error(f"Error occurred while handling monitoring event: {e}")
