from datetime import datetime

from sqlalchemy.orm import close_all_sessions

from src.handlers.monitors.common import (
    allow_notification,
    deserialize_sqs_record_to_device_models,
    send_device_monitor_messages,
    upsert_monitor_data,
)
from src.logger import logger
from src.models import DeviceModel, DeviceMonitorModel
from src.templates import (
    CASE_6_ABNORMAL_CONTENT,
    CASE_6_ABNORMAL_TITLE,
    CASE_6_NORMAL_CONTENT,
    CASE_6_NORMAL_TITLE,
    CASE_6_WARNING_CONTENT,
    CASE_6_WARNING_TITLE,
)
from src.types import DeviceStatus, EnableStatus, MonitorCases, MonitoringThresholds, MonitorStatus

MONITOR_CASE = MonitorCases.LONG_TERM_DISCONNECT
UNKNOWN = MonitorStatus.UNKNOWN
NORMAL = MonitorStatus.NORMAL
WARNING = MonitorStatus.WARNING
ABNORMAL = MonitorStatus.ABNORMAL


def set_notification_status(
    device_monitor: DeviceMonitorModel, device: DeviceModel, current_status: int, previous_status: int
):
    # Determine whether to send a notification based on the previous status and current status.
    if current_status == ABNORMAL and previous_status in (UNKNOWN, NORMAL, WARNING):
        device_monitor.push_firebase_message = True
        device_monitor.send_email = True
    if current_status == WARNING and previous_status in (UNKNOWN, NORMAL):
        device_monitor.push_firebase_message = True
    if device.is_push == EnableStatus.DISABLE:
        logger.debug(f"{device} related to {device_monitor} has `is_push`=`DISABLE`")
        device_monitor.push_firebase_message = False
    device_monitor.allow_notification = allow_notification(device_monitor, device)


def check_monitor_case_6_for_offline_devices(device: DeviceModel) -> DeviceMonitorModel | None:
    previous_status = device.long_disconnect_monitor_status

    time_delta_in_seconds = (datetime.utcnow() - device.sensor_time).total_seconds()
    if time_delta_in_seconds >= MonitoringThresholds.EMAIL_NOTIFICATION_DISCONNECT_DURATION:
        current_status = ABNORMAL
    elif time_delta_in_seconds >= MonitoringThresholds.APP_NOTIFICATION_DISCONNECT_DURATION:
        current_status = WARNING
    else:
        current_status = previous_status
    if current_status != previous_status:
        device.long_disconnect_monitor_status = current_status

    logger.debug(f"{device} long_disconnect_monitor_status: previous {previous_status}, current {current_status}")
    device_monitor = DeviceMonitorModel(
        imei=device.imei,
        occurred_at=datetime.utcnow(),
        monitor_case=MONITOR_CASE,
        monitor_status=current_status,
    )

    if current_status == ABNORMAL and previous_status in (UNKNOWN, NORMAL, WARNING):
        device_monitor.message = CASE_6_ABNORMAL_TITLE
        device_monitor.message_detail = CASE_6_ABNORMAL_CONTENT
    elif current_status == WARNING and previous_status in (UNKNOWN, NORMAL, ABNORMAL):
        device_monitor.message = CASE_6_WARNING_TITLE
        device_monitor.message_detail = CASE_6_WARNING_CONTENT
    else:
        # logger.debug(f"{device} does not match any conditions")
        return None

    set_notification_status(device_monitor, device, current_status, previous_status)
    return device_monitor


def check_monitor_case_6_for_online_devices(device: DeviceModel) -> DeviceMonitorModel | None:
    previous_status = device.long_disconnect_monitor_status

    time_delta_in_seconds = (datetime.utcnow() - device.sensor_time).total_seconds()
    if time_delta_in_seconds <= MonitoringThresholds.RECOVERY_CONNECTION_DURATION:
        current_status = NORMAL
        if current_status != previous_status:
            device.long_disconnect_monitor_status = current_status
    else:
        current_status = previous_status

    logger.debug(f"{device} long_disconnect_monitor_status: previous {previous_status}, current {current_status}")
    device_monitor = DeviceMonitorModel(
        imei=device.imei,
        occurred_at=datetime.utcnow(),
        monitor_case=MONITOR_CASE,
        monitor_status=current_status,
    )

    if current_status == NORMAL and previous_status in (ABNORMAL, WARNING):
        device_monitor.message = CASE_6_NORMAL_TITLE
        device_monitor.message_detail = CASE_6_NORMAL_CONTENT.format(
            co2=device.co2, temp=device.temp, humid=device.humid
        )
    elif current_status == NORMAL and previous_status == UNKNOWN:
        device_monitor.message = CASE_6_NORMAL_TITLE
        device_monitor.message_detail = CASE_6_NORMAL_CONTENT.format(
            co2=device.co2, temp=device.temp, humid=device.humid
        )
    else:
        # logger.debug(f"{device} does not match any conditions")
        return None

    set_notification_status(device_monitor, device, current_status, previous_status)
    return device_monitor


def process_monitoring_offline_devices(devices: list[DeviceModel]) -> (list[DeviceModel], list[DeviceMonitorModel]):
    updated_devices: list[DeviceModel] = []
    device_monitors: list[DeviceMonitorModel] = []

    for device in devices:
        if device_monitor := check_monitor_case_6_for_offline_devices(device):
            logger.debug(f"Generated {device_monitor}: {device_monitor.to_dict()}")
            device_monitors.append(device_monitor)
        if device.is_modified():
            updated_devices.append(device)

    return updated_devices, device_monitors


def process_monitoring_online_devices(devices: list[DeviceModel]) -> (list[DeviceModel], list[DeviceMonitorModel]):
    updated_devices: list[DeviceModel] = []
    device_monitors: list[DeviceMonitorModel] = []

    for device in devices:
        if device_monitor := check_monitor_case_6_for_online_devices(device):
            logger.debug(f"Generated {device_monitor}: {device_monitor.to_dict()}")
            device_monitors.append(device_monitor)
        if device.is_modified():
            updated_devices.append(device)

    return updated_devices, device_monitors


def handler(event, context):
    """:param event: SQS event"""
    batch_item_failures = []
    records = event.get("Records", [])
    logger.debug(f"Got {len(records)} SQS records")

    for record in records:
        try:
            # deserialize event.records
            devices = deserialize_sqs_record_to_device_models(record)
            device_status = record.get("messageAttributes", {}).get("device_status", {}).get("stringValue")
            logger.debug(f"Got {len(devices)} devices: {devices}, device_status: {device_status}")

            if str(device_status) == str(DeviceStatus.ONLINE):
                updated_devices, device_monitors = process_monitoring_online_devices(devices)
            else:
                updated_devices, device_monitors = process_monitoring_offline_devices(devices)
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
            logger.error(f"Failed: {e}")

    close_all_sessions()
    return {"batchItemFailures": batch_item_failures}
