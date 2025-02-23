from collections import defaultdict
from datetime import datetime, timedelta
from typing import Iterable

from sqlalchemy.orm import close_all_sessions

from src.handlers.monitors.common import (
    allow_notification,
    deserialize_sqs_record_to_device_models,
    device_repository,
    send_device_monitor_messages,
    statistic_repository,
    upsert_monitor_data,
)
from src.logger import logger
from src.models import DeviceModel, DeviceMonitorModel
from src.templates import CASE_5_ABNORMAL_CONTENT, CASE_5_ABNORMAL_TITLE, CASE_5_NORMAL_CONTENT, CASE_5_NORMAL_TITLE
from src.types import EnableStatus, MonitorCases, MonitoringThresholds, MonitorStatus

DEFAULT_ABSENCE_DURATION = 48  # hours
MONITOR_CASE = MonitorCases.LONG_TERM_ABSENCE
UNKNOWN = MonitorStatus.UNKNOWN
NORMAL = MonitorStatus.NORMAL
ABNORMAL = MonitorStatus.ABNORMAL


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


def check_normal_device(device: DeviceModel) -> DeviceMonitorModel | None:
    previous_status = device.long_absenc_monitor_status
    if device.last_statistic.co2_diff and abs(device.last_statistic.co2_diff) >= MonitoringThresholds.CO2_DIFF:
        current_status = NORMAL
        if current_status != previous_status:
            device.long_absenc_monitor_status = current_status
    else:
        current_status = previous_status

    logger.debug(f"{device} long_absenc_monitor_status: previous {previous_status}, current {current_status}")
    device_monitor = DeviceMonitorModel(
        imei=device.imei,
        occurred_at=datetime.utcnow(),
        monitor_case=MONITOR_CASE,
        monitor_status=current_status,
    )

    if current_status == NORMAL and previous_status == ABNORMAL:
        device_monitor.message = CASE_5_NORMAL_TITLE
        device_monitor.message_detail = CASE_5_NORMAL_CONTENT.format(
            co2=device.co2, temp=device.temp, humid=device.humid
        )
    elif current_status == NORMAL and previous_status == UNKNOWN:
        device_monitor.message = CASE_5_NORMAL_TITLE
        device_monitor.message_detail = CASE_5_NORMAL_CONTENT.format(
            co2=device.co2, temp=device.temp, humid=device.humid
        )
    else:
        # logger.debug(f"{device} does not match any conditions")
        return None

    set_notification_status(device_monitor, device, current_status, previous_status)
    return device_monitor


def check_abnormal_device(device: DeviceModel, abnormal_count: int, total_count: int) -> DeviceMonitorModel | None:
    alert_time = device.alert_setting.long_absenc_alert_time if device.alert_setting else DEFAULT_ABSENCE_DURATION
    previous_status = device.long_absenc_monitor_status

    if abnormal_count == total_count and abnormal_count >= alert_time * 12 * 0.8:
        current_status = ABNORMAL
        if current_status != previous_status:
            device.long_absenc_monitor_status = current_status
    else:
        current_status = previous_status

    logger.debug(
        f"{device} find out {total_count} records having "
        f"abs(co2_diff)>={MonitoringThresholds.CO2_DIFF} for {alert_time} hours. "
        f"long_absenc_monitor_status: previous {previous_status}, current {current_status}"
    )
    device_monitor = DeviceMonitorModel(
        imei=device.imei,
        occurred_at=datetime.utcnow(),
        monitor_case=MONITOR_CASE,
        monitor_status=current_status,
    )

    if current_status == ABNORMAL and previous_status in (NORMAL, UNKNOWN):
        device_monitor.message = CASE_5_ABNORMAL_TITLE
        device_monitor.message_detail = CASE_5_ABNORMAL_CONTENT.format(
            co2=device.co2, temp=device.temp, humid=device.humid, setting_time=alert_time
        )
        set_notification_status(device_monitor, device, current_status, previous_status)
        return device_monitor
    # logger.debug(f"{device} does not match any conditions")


def group_devices_by_absence_duration(devices: Iterable[DeviceModel]) -> dict[str : list[DeviceModel]]:
    # devices group by alert_setting.long_absenc_alert_time
    device_repository.load_alert_settings(devices)
    groups = defaultdict(lambda: [])
    for device in devices:
        alert_time = device.alert_setting.long_absenc_alert_time if device.alert_setting else DEFAULT_ABSENCE_DURATION
        groups[alert_time].append(device)
    return groups


def classify_devices(devices: list[DeviceModel]) -> (list[DeviceModel], list[DeviceModel]):
    normal_devices: list[DeviceModel] = []
    abnormal_devices: list[DeviceModel] = []
    device_repository.load_last_statistics(devices)

    for device in devices:
        if device.last_statistic.co2_diff is None:
            continue
        elif abs(device.last_statistic.co2_diff) >= MonitoringThresholds.CO2_DIFF:
            normal_devices.append(device)
        else:
            abnormal_devices.append(device)
    return normal_devices, abnormal_devices


def process_monitoring_abnormal_devices(devices: list[DeviceModel]) -> (list[DeviceModel], list[DeviceMonitorModel]):
    updated_devices: list[DeviceModel] = []
    device_monitors: list[DeviceMonitorModel] = []

    device_groups = group_devices_by_absence_duration(devices)
    now = datetime.utcnow()

    for duration, devices in device_groups.items():
        # count the number of Statistic records having abs(co2_diff) <= 35 for {alert_time} hours
        stats = statistic_repository.count_co2_diff_below_threshold(
            imeis=(i.imei for i in devices),
            since=now - timedelta(hours=duration),
            until=now,
            threshold=MonitoringThresholds.CO2_DIFF,
        )
        stats_mapping = {imei: (match, total) for imei, match, total in stats}
        logger.debug(
            f"Checking {len(devices)} Devices for {duration} hours ago. "
            f"Exceeding-threshold count : {stats_mapping}"
        )

        for device in devices:
            abnormal_count, total_count = stats_mapping.get(device.imei, {})
            if device_monitor := check_abnormal_device(device, abnormal_count, total_count):
                logger.debug(f"Generated {device_monitor}: {device_monitor.to_dict()}")
                device_monitors.append(device_monitor)
            if device.is_modified():
                updated_devices.append(device)
    return updated_devices, device_monitors


def process_monitoring_normal_devices(devices: list[DeviceModel]) -> (list[DeviceModel], list[DeviceMonitorModel]):
    updated_devices: list[DeviceModel] = []
    device_monitors: list[DeviceMonitorModel] = []

    for device in devices:
        if device_monitor := check_normal_device(device):
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
            # deserialize event.record
            devices = deserialize_sqs_record_to_device_models(record)
            logger.info(f"Got {len(devices)} devices: {devices}")

            # classify devices depend on staitstic.co2_diff
            normal_devices, abnormal_devices = classify_devices(devices)
            logger.info(
                f"Got {len(normal_devices)} normal_devices: {normal_devices}, "
                f"Got {len(abnormal_devices)} abnormal_devices: {abnormal_devices}"
            )

            updated_normal_devices, normal_device_monitors = process_monitoring_normal_devices(normal_devices)
            updated_abnormal_devices, abnormal_device_monitors = process_monitoring_abnormal_devices(abnormal_devices)
            updated_devices = [*updated_normal_devices, *updated_abnormal_devices]
            device_monitors = [*normal_device_monitors, *abnormal_device_monitors]
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
