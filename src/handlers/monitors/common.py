from typing import Any

from src.constants import COMPRESS_SIZE, SQS_NOTIFICATION_URL
from src.logger import logger
from src.models import DeviceModel, DeviceMonitorModel
from src.repositories import DeviceMonitorRepository, DeviceRepository, StatisticRepository
from src.services.sqs import SqsService
from src.types import DeviceState

device_repository = DeviceRepository()
device_monitor_repository = DeviceMonitorRepository()
statistic_repository = StatisticRepository()
sqs_service = SqsService()


def deserialize_sqs_record_to_device_models(record: Any) -> list[DeviceModel]:
    # logger.debug(f"Deserialize record: {record}")
    try:
        # parse JSON
        unverified_devices = device_repository.deserialize_sqs_record(record)
        imeis = [device.imei for device in unverified_devices]
        devices = device_repository.list_devices_by_imei(imeis)
        return devices
    except Exception as e:
        logger.error(f"Failed to deserialize record {record}: {e}")
        raise e


def send_device_monitor_messages(device_monitors: list[DeviceMonitorModel]):
    if device_monitors:
        messages = device_monitor_repository.to_sqs_messages(device_monitors, compress_size=COMPRESS_SIZE)
        sqs_service.send_messages(SQS_NOTIFICATION_URL, messages)


def allow_notification(device_monitor: DeviceMonitorModel, device: DeviceModel):
    if not device.account_id:
        logger.debug(f"The {device} related to {device_monitor} has account_id=`null`")
        return False
    if device.device_state == DeviceState.STOP_MONITORING:
        logger.debug(f"The {device} related to {device_monitor} has been STOP_MONITORING")
        return False
    if not device_monitor.push_firebase_message and not device_monitor.send_email:
        logger.debug(f"{device_monitor} has both `push_firebase_message` and `send_email` set to `false`")
        return False
    return True


def upsert_monitor_data(
    devices: list[DeviceModel] | None = None, device_monitors: list[DeviceMonitorModel] | None = None
):
    if devices:
        # logger.debug(f"Updating {len(devices)} Devices: {devices}")
        device_repository.bulk_update(models=devices)

    if device_monitors:
        # logger.debug(f"Inserting {len(device_monitors)} DeviceMonitors: {device_monitors}")
        device_monitor_repository.bulk_create(models=device_monitors, return_defaults=True)
