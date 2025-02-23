from datetime import datetime, timedelta

from sqlalchemy.orm import close_all_sessions

from src.handlers.monitors.common import (
    allow_notification,
    deserialize_sqs_record_to_device_models,
    device_monitor_repository,
    device_repository,
    send_device_monitor_messages,
    upsert_monitor_data,
)
from src.logger import logger
from src.models import DeviceModel, DeviceMonitorModel
from src.templates import CASE_7_ABNORMAL_CONTENT, CASE_7_ABNORMAL_TITLE
from src.types import DeviceState, EnableStatus, MonitorCases, MonitoringThresholds, MonitorStatus

RECOVERY_DURATION = timedelta(hours=4)
MONITOR_CASE = MonitorCases.SUSPICIOUS_INTRUDER
UNKNOWN = MonitorStatus.UNKNOWN
NORMAL = MonitorStatus.NORMAL
ABNORMAL = MonitorStatus.ABNORMAL


def classify_devices(devices: list[DeviceModel]) -> (list[DeviceModel], list[DeviceModel]):
    recovery_devices: list[DeviceModel] = []
    absented_devices: list[DeviceModel] = []
    now = datetime.utcnow()

    previous_device_monitors = device_monitor_repository.get_last_device_monitors(
        (item.imei for item in devices if item.intruder_monitor_status == ABNORMAL),
        [MONITOR_CASE],
    )
    device_monitor_mapping = {item.imei: item for item in previous_device_monitors}

    for device in devices:
        if device.device_state == DeviceState.ABSENCE:
            # filter recovery_devices
            if previous_device_monitor := device_monitor_mapping.get(device.imei):
                if now - previous_device_monitor.occurred_at >= RECOVERY_DURATION:
                    recovery_devices.append(device)
                    continue

            absented_devices.append(device)

    return recovery_devices, absented_devices


def set_notification_status(
    device_monitor: DeviceMonitorModel, device: DeviceModel, current_status: int, previous_status: int
):
    # Determine whether to send a notification based on the previous status and current status.
    if current_status == ABNORMAL and previous_status in (UNKNOWN, NORMAL):
        device_monitor.push_firebase_message = True
        device_monitor.send_email = True

    if device.is_push == EnableStatus.DISABLE:
        logger.debug(f"{device} related to {device_monitor} has `is_push`=`DISABLE`")
        device_monitor.push_firebase_message = False
    device_monitor.allow_notification = allow_notification(device_monitor, device)


def process_monitoring_recovery_devices(devices: list[DeviceModel]) -> (list[DeviceModel], list[DeviceMonitorModel]):
    device_monitors: list[DeviceMonitorModel] = []

    for device in devices:
        current_status = NORMAL
        previous_status = device.intruder_monitor_status
        logger.debug(f"{device} intruder_monitor_status: previous {previous_status}, current {current_status}")

        if previous_status != NORMAL:
            # logger.debug(f"{device} set intruder_monitor_status=NORMAL")
            device.intruder_monitor_status = NORMAL

    return devices, device_monitors


def process_monitoring_absented_devices(devices: list[DeviceModel]) -> (list[DeviceModel], list[DeviceMonitorModel]):
    updated_devices: list[DeviceModel] = []
    device_monitors: list[DeviceMonitorModel] = []

    for device in devices:
        previous_status = device.intruder_monitor_status

        if statistic := device.last_statistic:
            if statistic.co2_diff and statistic.co2_diff >= MonitoringThresholds.CO2_DIFF:
                current_status = ABNORMAL
                if current_status != previous_status:
                    device.intruder_monitor_status = current_status
                    updated_devices.append(device)
            else:
                current_status = previous_status

            logger.debug(
                f"Statistic<id={statistic.id}, co2_diff={statistic.co2_diff}>, "
                f"{device}: previous_status {previous_status}, current_status {current_status}"
            )

            if current_status == ABNORMAL and previous_status in (UNKNOWN, NORMAL):
                device_monitor = DeviceMonitorModel(
                    imei=device.imei,
                    occurred_at=datetime.utcnow(),
                    monitor_case=MONITOR_CASE,
                    monitor_status=current_status,
                    message=CASE_7_ABNORMAL_TITLE,
                    message_detail=CASE_7_ABNORMAL_CONTENT,
                )
                set_notification_status(device_monitor, device, current_status, previous_status)
                device_monitors.append(device_monitor)
            # else:
            # logger.debug(f"{device} does not match any conditions")
        else:
            logger.debug(f"{device} has no statistic")

    return updated_devices, device_monitors


def handler(event, context):
    """:param event: SQS event"""
    batch_item_failures = []
    records = event.get("Records", [])
    logger.debug(f"Got {len(records)} SQS records")

    for record in records:
        try:
            # deserialize event.record
            devices = deserialize_sqs_record_to_device_models(record)
            logger.info(f"Got {len(devices)} devices: {devices}")

            # absenting_devices: device has device_state=`ABSENCE` but hasn't absented
            # absented_devices: device has been absented less than 4 hours
            # recovery_devices: device has been absented more than or equal to 4 hours
            recovery_devices, absented_devices = classify_devices(devices)
            logger.info(
                f"Got {len(recovery_devices)} recovery_devices: {recovery_devices}, "
                f"Got {len(absented_devices)} absented_devices: {absented_devices}"
            )

            device_repository.load_last_statistics(absented_devices)
            updated_recovery_devices, recovery_device_monitors = process_monitoring_recovery_devices(recovery_devices)
            updated_absented_devices, absented_device_monitors = process_monitoring_absented_devices(absented_devices)

            updated_devices = [*updated_recovery_devices, *updated_absented_devices]
            device_monitors = [*recovery_device_monitors, *absented_device_monitors]
            logger.info(
                f"Updated {len(updated_devices)} Device models: {updated_devices}, "
                f"Created {len(device_monitors)} DeviceMonitor models: {device_monitors}"
            )

            upsert_monitor_data(updated_devices, device_monitors)
            logger.info(
                f"Updated {len(devices)} Devices successfully: {devices}, "
                f"Inserted {len(device_monitors)} DeviceMonitors successfully: {device_monitors}"
            )

            # send notifications
            device_monitor_to_send = list(filter(lambda item: item.allow_notification, device_monitors))
            logger.debug(f"DeviceMonitor to send: {device_monitor_to_send}")
            send_device_monitor_messages(device_monitor_to_send)
            # logger.info("Send Notifications successfully")
        except Exception as e:
            batch_item_failures.append(record["messageId"])
            logger.error(f"Failed - {e}")

    close_all_sessions()
    return {"batchItemFailures": batch_item_failures}
