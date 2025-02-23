from sqlalchemy.orm import close_all_sessions

from src.logger import logger
from src.repositories import DeviceRepository
from src.utils import get_imei_from_topic

device_repository = DeviceRepository()


def handler(event, context):
    imei = get_imei_from_topic(event.get("topic", ""))
    event_type = event.get("event")
    version = event.get("version")

    if not imei or not version or event_type != 1:
        logger.error(f"Invalid event<imei={imei}, event={event_type}, version={version}>: {event}")
        return None

    try:
        if device := device_repository.get(imei):
            logger.info(f"Found {device}")
            # update device
            if device.firmware_version != version:
                device.firmware_version = version
                device_repository.save(device)
                logger.info(f"Updated Device<imei={imei}, version={version}> successfully")
        else:
            logger.warning(f"Device<imei={imei}> not found")
    except Exception as e:
        logger.error(f"`update_firmware` IMEI#{imei}: {e}")

    close_all_sessions()
