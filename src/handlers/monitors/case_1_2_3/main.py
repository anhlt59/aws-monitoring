from datetime import datetime, timedelta
from typing import Iterable

from sqlalchemy.orm import close_all_sessions

from src import templates
from src.handlers.monitors.common import (
    allow_notification,
    deserialize_sqs_record_to_device_models,
    send_device_monitor_messages,
    statistic_repository,
    upsert_monitor_data,
)
from src.logger import logger
from src.models import DeviceModel, DeviceMonitorModel, StatisticModel
from src.types import EnableStatus, MonitorCases, MonitoringThresholds, MonitorStatus

# A minimum number of items used to determine whether to create a device_monitor or not.
MIN_COUNT = 5
TRACKING_DURATION = timedelta(minutes=30)
UNKNOWN = MonitorStatus.UNKNOWN
NORMAL = MonitorStatus.NORMAL
WARNING = MonitorStatus.WARNING
ABNORMAL = MonitorStatus.ABNORMAL


def count_statistics(values: Iterable[int | float], warning_threshold: int | float, abnormal_threshold: int | float):
    normal_count = 0
    warning_count = 0
    abnormal_count = 0
    for value in values:
        if value < warning_threshold:
            normal_count += 1
        elif warning_threshold <= value < abnormal_threshold:
            warning_count += 1
        elif value >= abnormal_threshold:
            abnormal_count += 1
            warning_count += 1
    return normal_count, warning_count, abnormal_count


def count_case_3_statistics(statistics: Iterable[StatisticModel]):
    normal_count = 0
    warning_count = 0
    abnormal_count = 0
    for stats in statistics:
        if stats.temp < MonitoringThresholds.HEATSTROKE_TEMP_WARNING:
            normal_count += 1
        elif (
            MonitoringThresholds.HEATSTROKE_TEMP_WARNING <= stats.temp < MonitoringThresholds.HEATSTROKE_TEMP_ABNORMAL
            and stats.humid > MonitoringThresholds.HEATSTROKE_HUMID_WARNING
        ):
            warning_count += 1
        elif stats.temp >= MonitoringThresholds.HEATSTROKE_TEMP_ABNORMAL:
            abnormal_count += 1
            warning_count += 1
    return normal_count, warning_count, abnormal_count


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


def check_monitor_case_1(device: DeviceModel, statistics: list[StatisticModel]) -> DeviceMonitorModel | None:
    if len(statistics) < MIN_COUNT:
        logger.debug(f"{device} skip checking (statistics-count < {MIN_COUNT})")
        return None

    # Count statistics
    normal_count, warning_count, abnormal_count = count_statistics(
        (stats.co2 for stats in statistics),
        warning_threshold=MonitoringThresholds.CO2_WARNING,
        abnormal_threshold=MonitoringThresholds.CO2_ABNORMAL,
    )

    previous_status = device.co2_monitor_status
    if abnormal_count >= MIN_COUNT:
        current_status = ABNORMAL
    elif warning_count >= MIN_COUNT:
        current_status = WARNING
    elif normal_count >= MIN_COUNT:
        current_status = NORMAL
    else:
        current_status = previous_status
    if current_status != previous_status:
        device.co2_monitor_status = current_status

    logger.debug(
        f"{device} case 1: normal={normal_count}, warning={warning_count}, abnormal={abnormal_count}, "
        f"previous_status={previous_status}, current_status={current_status}"
    )

    device_monitor = DeviceMonitorModel(
        imei=device.imei,
        occurred_at=datetime.utcnow(),
        monitor_case=MonitorCases.CO2,
        monitor_status=current_status,
    )

    if current_status == ABNORMAL and previous_status in (UNKNOWN, NORMAL, WARNING):
        device_monitor.message = templates.CASE_1_ABNORMAL_TITLE
        device_monitor.message_detail = templates.CASE_1_ABNORMAL_CONTENT.format(value=device.co2)
    elif current_status == WARNING and previous_status in (UNKNOWN, NORMAL, ABNORMAL):
        device_monitor.message = templates.CASE_1_WARNING_TITLE
        device_monitor.message_detail = templates.CASE_1_WARNING_CONTENT.format(value=device.co2)
    elif current_status == NORMAL and previous_status in (ABNORMAL, WARNING):
        device_monitor.message = templates.CASE_1_NORMAL_TITLE
        device_monitor.message_detail = templates.CASE_1_NORMAL_CONTENT
    elif current_status == NORMAL and previous_status == UNKNOWN:
        device_monitor.message = templates.CASE_1_NORMAL_TITLE
        device_monitor.message_detail = templates.CASE_1_NORMAL_CONTENT
    else:
        # logger.debug(f"{device} does not match any conditions")
        return None

    set_notification_status(device_monitor, device, current_status, previous_status)
    return device_monitor


def check_monitor_case_2(device: DeviceModel, statistics: list[StatisticModel]) -> DeviceMonitorModel | None:
    # Count statistics
    normal_count, warning_count, abnormal_count = count_statistics(
        (stats.temp for stats in statistics),
        warning_threshold=MonitoringThresholds.TEMP_WARNING,
        abnormal_threshold=MonitoringThresholds.TEMP_ABNORMAL,
    )

    previous_status = device.temp_monitor_status
    # the minimum value of abnormal_count is an exclusion, it's fixed to 1

    if abnormal_count == 0 and len(statistics) < MIN_COUNT:
        logger.debug(f"{device} skip checking (statistics-count < {MIN_COUNT})")
        return None
    if abnormal_count >= 1:
        current_status = ABNORMAL
    elif warning_count >= MIN_COUNT:
        current_status = WARNING
    elif normal_count >= MIN_COUNT:
        current_status = NORMAL
    else:
        current_status = previous_status
    if current_status != previous_status:
        device.temp_monitor_status = current_status

    logger.debug(
        f"{device} case 2: normal={normal_count}, warning={warning_count}, abnormal={abnormal_count}, "
        f"previous_status={previous_status}, current_status={current_status}"
    )

    device_monitor = DeviceMonitorModel(
        imei=device.imei,
        occurred_at=datetime.utcnow(),
        monitor_case=MonitorCases.TEMPERATURE,
        monitor_status=current_status,
    )

    if current_status == ABNORMAL and previous_status in (UNKNOWN, NORMAL, WARNING):
        device_monitor.message = templates.CASE_2_ABNORMAL_TITLE
        device_monitor.message_detail = templates.CASE_2_ABNORMAL_CONTENT.format(value=device.temp)
    elif current_status == WARNING and previous_status in (UNKNOWN, NORMAL, ABNORMAL):
        device_monitor.message = templates.CASE_2_WARNING_TITLE
        device_monitor.message_detail = templates.CASE_2_WARNING_CONTENT.format(value=device.temp)
    elif current_status == NORMAL and previous_status in (ABNORMAL, WARNING):
        device_monitor.message = templates.CASE_2_NORMAL_TITLE
        device_monitor.message_detail = templates.CASE_2_NORMAL_CONTENT
    elif current_status == NORMAL and previous_status == UNKNOWN:
        device_monitor.message = templates.CASE_2_NORMAL_TITLE
        device_monitor.message_detail = templates.CASE_2_NORMAL_CONTENT
    else:
        # logger.debug(f"{device} does not match any conditions")
        return None

    set_notification_status(device_monitor, device, current_status, previous_status)
    return device_monitor


def check_monitor_case_3(device: DeviceModel, statistics: list[StatisticModel]) -> DeviceMonitorModel | None:
    if len(statistics) < MIN_COUNT:
        logger.debug(f"{device} skip checking (statistics-count < {MIN_COUNT})")
        return None

    # Count statistics
    normal_count, warning_count, abnormal_count = count_case_3_statistics(statistics)

    previous_status = device.heat_stroke_monitor_status
    if abnormal_count >= MIN_COUNT:
        current_status = ABNORMAL
    elif warning_count >= MIN_COUNT:
        current_status = WARNING
    elif normal_count >= MIN_COUNT:
        current_status = NORMAL
    else:
        current_status = previous_status
    if current_status != previous_status:
        device.heat_stroke_monitor_status = current_status

    logger.debug(
        f"{device} case 3: normal={normal_count}, warning={warning_count}, abnormal={abnormal_count}, "
        f"previous_status={previous_status}, current_status={current_status}"
    )

    device_monitor = DeviceMonitorModel(
        imei=device.imei,
        occurred_at=datetime.utcnow(),
        monitor_case=MonitorCases.HEATSTROKE,
        monitor_status=current_status,
    )

    if current_status == ABNORMAL and previous_status in (UNKNOWN, NORMAL, WARNING):
        device_monitor.message = templates.CASE_3_ABNORMAL_TITLE
        device_monitor.message_detail = templates.CASE_3_ABNORMAL_CONTENT.format(
            co2=device.co2, temp=device.temp, humid=device.humid
        )
    elif current_status == WARNING and previous_status in (UNKNOWN, NORMAL, ABNORMAL):
        device_monitor.message = templates.CASE_3_WARNING_TITLE
        device_monitor.message_detail = templates.CASE_3_WARNING_CONTENT.format(
            co2=device.co2, temp=device.temp, humid=device.humid
        )
    elif current_status == NORMAL and previous_status in (ABNORMAL, WARNING):
        device_monitor.message = templates.CASE_3_NORMAL_TITLE
        device_monitor.message_detail = templates.CASE_3_NORMAL_CONTENT.format(
            co2=device.co2, temp=device.temp, humid=device.humid
        )
    elif current_status == NORMAL and previous_status == UNKNOWN:
        device_monitor.message = templates.CASE_3_NORMAL_TITLE
        device_monitor.message_detail = templates.CASE_3_NORMAL_CONTENT.format(
            co2=device.co2, temp=device.temp, humid=device.humid
        )
    else:
        # logger.debug(f"{device} does not match any conditions")
        return None

    set_notification_status(device_monitor, device, current_status, previous_status)
    return device_monitor


def process_monitoring(
    devices: list[DeviceModel], tracking_duration: timedelta
) -> (list[DeviceModel], list[DeviceMonitorModel]):
    updated_devices: list[DeviceModel] = []
    device_monitors: list[DeviceMonitorModel] = []

    until = datetime.utcnow()
    since = until - tracking_duration
    statistics = statistic_repository.group_statistics_by_imei(
        (device.imei for device in devices), since=since, until=until
    )

    for device in devices:
        device_stats = statistics.get(device.imei, [])
        logger.debug(f"{device} has {len(device_stats)} statistics: {statistic_repository.to_json(device_stats)}")

        for device_monitor in (
            check_monitor_case_1(device, device_stats),
            check_monitor_case_2(device, device_stats),
            check_monitor_case_3(device, device_stats),
        ):
            if device_monitor:
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

            updated_devices, device_monitors = process_monitoring(devices, TRACKING_DURATION)
            logger.info(
                f"Updated {len(updated_devices)} Device models: {updated_devices}, "
                f"Created {len(device_monitors)} DeviceMonitor models: {device_monitors}"
            )

            upsert_monitor_data(updated_devices, device_monitors)
            logger.info(
                f"Updated {len(updated_devices)} Devices successfully: {updated_devices},"
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
