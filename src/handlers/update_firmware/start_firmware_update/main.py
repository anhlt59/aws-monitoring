from sqlalchemy.orm import close_all_sessions

from src.logger import logger
from src.repositories import DeviceRepository
from src.services.devices import DeviceService
from src.services.iot_core import IotDataService
from src.services.storage import StorageService

device_service = DeviceService(
    device_repository=DeviceRepository(),
    iot_service=IotDataService(),
    storage_service=StorageService(),
)


def handler(event, context):
    fw_info = device_service.get_firmware_info()
    total = 0

    # publish message to iot_core
    for device in device_service.list_all_devices_below_version(fw_info.version):
        total += 1
        device_service.start_firmware_update(fw_info, device)

    logger.info(f"Sent messages to {total} devices")
    close_all_sessions()
