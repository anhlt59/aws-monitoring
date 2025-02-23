from src.logger import logger
from src.utils import get_imei_from_topic


def handler(event, context):
    event_type = event.get("event")
    if event_type == 2:
        imei = get_imei_from_topic(event.get("topic", ""))
        logger.info(f"Device<imei={imei}> firmware updated")
    else:
        logger.error(f"Invalid event<{event_type}>: {event}")
