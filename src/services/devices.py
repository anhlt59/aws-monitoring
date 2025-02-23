import csv
import io
import json
from dataclasses import dataclass
from typing import Iterable

from src.constants import S3_BUCKET_NAME, S3_FIRMWARE_INFO_KEY
from src.logger import logger
from src.models import DeviceModel
from src.repositories.devices import DeviceRepository
from src.services.iot_core import IotDataService
from src.services.storage import StorageService
from src.utils import parse_version


@dataclass
class FirmwareInfo:
    version: str
    url: str
    fw_name: str = "app_update.bin"
    ota: int = 1


class DeviceService:
    def __init__(
        self, device_repository: DeviceRepository, iot_service: IotDataService, storage_service: StorageService
    ):
        self.device_repository = device_repository
        self.iot = iot_service
        self.storage = storage_service

    def get_firmware_info(self) -> FirmwareInfo:
        """Get firmware version info, that is stored in the S3 bucket as a CSV file."""
        context = self.storage.get_object(S3_FIRMWARE_INFO_KEY, S3_BUCKET_NAME)
        csv_file = io.StringIO(context)
        reader = csv.DictReader(csv_file)
        if rows := list(reader):
            return FirmwareInfo(**rows[0])
        raise Exception("Invalid firmware info")

    def start_firmware_update(self, fw_info: FirmwareInfo, device: DeviceModel):
        if device.firmware_version is None or parse_version(fw_info.version) > parse_version(device.firmware_version):
            # publish message to iot_core
            payload = json.dumps(
                {
                    "version": fw_info.version,
                    "url": fw_info.url,
                    "fw_name": "app_update.bin",
                    "ota": 1,
                    "event": 2,
                }
            )
            self.iot.publish(topic=f"/nb/{device.imei}/notify", payload=payload)

    def check_firmware_version(self, fw_info: FirmwareInfo, device: DeviceModel):
        if device.firmware_version is None or parse_version(fw_info.version) > parse_version(device.firmware_version):
            # publish message to iot_core
            payload = json.dumps({"event": 1})
            self.iot.publish(topic=f"/nb/{device.imei}/notify", payload=payload)

    def list_all_devices_below_version(self, version: str) -> Iterable[DeviceModel]:
        limit = 200
        offset = 0

        while True:
            devices = self.device_repository.list_devices_below_version(version, limit, offset)
            logger.debug(f"Got {len(devices)} devices below version {version}")
            yield from devices
            if (length := len(devices)) < limit:
                break
            offset += length
