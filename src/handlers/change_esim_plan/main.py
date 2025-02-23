from datetime import datetime, timedelta

from sqlalchemy.orm import close_all_sessions

from src.logger import logger
from src.models import DeviceModel
from src.repositories import DeviceRepository
from src.services.devices import DeviceService
from src.services.iot_core import IotDataService
from src.services.soracom import SoracomService
from src.services.storage import StorageService

TARGET_PLAN = "planX3"

soracom_service = SoracomService()
device_repository = DeviceRepository()
device_service = DeviceService(
    device_repository,
    iot_service=IotDataService(),
    storage_service=StorageService(),
)


def update_device(device: DeviceModel):
    device.sim_plan = TARGET_PLAN
    device.started_at = datetime.utcnow()
    device.expired_at = device.started_at + timedelta(days=365)
    # logger.debug(f"{device}: {device.to_dict()}")
    device_repository.save(device)


def handler(event, context):
    sim_id = event.get("parameter1")
    old_status = event.get("parameter2")
    new_status = event.get("parameter3")

    if not sim_id:
        logger.warning("sim_id not found")
    elif old_status != "standby" and new_status != "active":
        logger.warning(f"old_status ({old_status}) & new_status ({new_status}) are incorect")
    else:
        logger.info(f"Got event for SIM<{sim_id}>")
        try:
            # change SIM plan
            soracom_service.add_subscription(sim_id, {"subscription": TARGET_PLAN})
            logger.info(f"Changed Soracom SIM#{sim_id} plan to {TARGET_PLAN}")

            # update device record
            if device := device_repository.get_by(sim_id=sim_id):
                logger.debug(f"Found {device}")
                update_device(device)
                logger.info(f"{device} updated sim_plan={TARGET_PLAN} successfully")

                # get firmware info from S3
                fw_info = device_service.get_firmware_info()

                # publish message to iot_core
                logger.info(f"Start firmware update for {device} to version={fw_info.version}")
                device_service.start_firmware_update(fw_info, device)
            else:
                logger.warning(f"Device<sim_id={sim_id}> not found")

        except Exception as e:
            logger.error(e)

    close_all_sessions()
