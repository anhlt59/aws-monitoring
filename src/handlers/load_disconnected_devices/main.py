from sqlalchemy.orm import close_all_sessions

from src.constants import DB_DEFAULT_UPDATE_BATCH_SIZE, SQS_MONITOR_6_URL, STAGE
from src.logger import logger
from src.models import DeviceModel
from src.repositories import DeviceRepository
from src.services.soracom import SoracomService
from src.services.sqs import SqsService
from src.types import DeviceStatus
from src.utils import chunks

SORACOM_LIMIT_SIZE = 100

device_repository = DeviceRepository()
sqs_service = SqsService()
soracom_service = SoracomService()


def check_soracom_sim_status(devices: list[DeviceModel]) -> list[DeviceModel]:  # noqa
    updated_devices = []

    if STAGE == "dev":
        # TODO: testing------------------------------------
        for device in devices:
            if device.device_status != DeviceStatus.OFFLINE:
                device.device_status = DeviceStatus.OFFLINE
                updated_devices.append(device)
                logger.debug(
                    f"The Sim<id={device.sim_id}> status returned from Soracom is OFFLINE, "
                    f"{device} updated device_status={device.device_status}"
                )

    else:
        # get SIM info from soracom, then update device_status
        mapping = {device.sim_id: device for device in devices}
        sim_ids = mapping.keys()
        for chunked_sim_ids in chunks(sim_ids, SORACOM_LIMIT_SIZE):
            try:
                sims = soracom_service.search_sims(sim_ids=chunked_sim_ids)
                verified_sim_id = (item.get("simId") for item in sims)

                if not_exists_sim_ids := set(chunked_sim_ids) - set(verified_sim_id):
                    logger.warning(f"SimIds not found: {not_exists_sim_ids}")
            except Exception as e:
                logger.error(f"Failed to search soracom sims {chunked_sim_ids}: {e}")
                continue

            for sim in sims:
                if device := mapping.get(sim.get("simId")):
                    if sim.get("sessionStatus", {}).get("online") is False:
                        # sessionStatus.online = false > device_status is OFFLINE
                        if device.device_status != DeviceStatus.OFFLINE:
                            logger.info(
                                f"The Sim<id={device.sim_id}> status returned from Soracom is OFFLINE, "
                                f"{device} updated device_status {device.device_status} to {DeviceStatus.OFFLINE}"
                            )
                            device.device_status = DeviceStatus.OFFLINE
                            updated_devices.append(device)
                    else:
                        # sessionStatus.online = true > device_status is ABNORMAL
                        if device.device_status != DeviceStatus.ABNORMAL:
                            logger.info(
                                f"The Sim<id={device.sim_id}> status returned from Soracom is ONLINE, "
                                f"{device} updated device_status {device.device_status} to {DeviceStatus.OFFLINE}"
                            )
                            device.device_status = DeviceStatus.ABNORMAL
                            updated_devices.append(device)

    return updated_devices


def handler(event, context):
    try:
        # get abnormal devices from `devices` table which haven't received any update for 10 minutes
        if disconnected_devices := device_repository.list_disconnected_devices(offline_duration=10):
            logger.info(
                f"Got {len(disconnected_devices)} devices have been disconnected for more than 10 mins:"
                f" {disconnected_devices}"
            )
            for chunked_devices in chunks(disconnected_devices, DB_DEFAULT_UPDATE_BATCH_SIZE):
                # check device info from soracom
                if updated_devices := check_soracom_sim_status(chunked_devices):
                    # , then update device_status
                    device_repository.bulk_update(models=updated_devices)
                    logger.info(f"Updated {len(updated_devices)} Devices successfully: {updated_devices}")

            # create sqs messages
            messages = device_repository.to_sqs_messages(
                disconnected_devices,
                message_attributes={"device_status": {"DataType": "Number", "StringValue": str(DeviceStatus.OFFLINE)}},
            )
            # logger.info(f"Sending {len(messages)} messages to SQS<{SQS_MONITOR_6_URL}>")
            # send messages to SQS_MONITOR_6_URL queue
            sqs_service.send_messages(SQS_MONITOR_6_URL, messages)
            # logger.info(f"Sent {len(messages)} messages to SQS<{SQS_MONITOR_6_URL}> successfully")
        else:
            logger.info("All devices are fine")

    except Exception as e:
        logger.error(f"Failed: {e}")

    close_all_sessions()
