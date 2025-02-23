from sqlalchemy.orm import close_all_sessions

from src.constants import SQS_MONITOR_7_URL
from src.logger import logger
from src.repositories import DeviceRepository
from src.services.sqs import SqsService

device_repository = DeviceRepository()
sqs_service = SqsService()


def handler(event, context):
    try:
        # get recover absent devices from `devices` table which has device_state=`ABSENCE` and
        # intruder_monitor_status=`ABNORMAL` and absented_at occurred 4 hours ago
        if recover_devices := device_repository.list_absent_devices():
            logger.info(f"Got {len(recover_devices)} recover devices: {recover_devices}")
            # create sqs messages
            messages = device_repository.to_sqs_messages(recover_devices)
            # send messages to SQS_MONITOR_6_URL queue
            sqs_service.send_messages(SQS_MONITOR_7_URL, messages)
            # logger.info(f"Sent {len(messages)} messages to SQS<{SQS_MONITOR_7_URL}> successfully")
        else:
            logger.info("All devices are fine")
    except Exception as e:
        logger.error(f"Failed: {e}")

    close_all_sessions()
