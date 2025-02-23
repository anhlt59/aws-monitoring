from datetime import datetime, timedelta

from sqlalchemy.orm import close_all_sessions

from src.handlers.monitors.common import (
    deserialize_sqs_record_to_device_models,
    statistic_repository,
    upsert_monitor_data,
)
from src.logger import logger
from src.models import DeviceModel, DeviceMonitorModel, StatisticModel
from src.templates import CASE_4_NORMAL_CONTENT, CASE_4_NORMAL_TITLE, CASE_4_WARNING_CONTENT, CASE_4_WARNING_TITLE
from src.types import MonitorCases, MonitoringThresholds, MonitorStatus

MIN_COUNT = 5
TRACKING_DURATION = timedelta(minutes=30)
MONITOR_CASE = MonitorCases.INFLUENZA
UNKNOWN = MonitorStatus.UNKNOWN
NORMAL = MonitorStatus.NORMAL
WARNING = MonitorStatus.WARNING


def count_statistics(statistics: list[StatisticModel], temp_threshold: float, hum_threshold: float):
    normal_count = 0
    warning_count = 0

    for statistic in statistics:
        if statistic.temp < temp_threshold and statistic.humid < hum_threshold:
            warning_count += 1
        elif statistic.temp >= temp_threshold or statistic.humid >= hum_threshold:
            normal_count += 1
    return normal_count, warning_count


def check_monitor_case_4(device: DeviceModel, statistics: list[StatisticModel]) -> DeviceMonitorModel | None:
    # check monitoring case 4
    normal_count, warning_count = count_statistics(
        statistics, MonitoringThresholds.INFLUENZA_TEMP, MonitoringThresholds.INFLUENZA_HUM
    )

    previous_status = device.influenza_monitor_status
    if warning_count >= MIN_COUNT:
        current_status = WARNING
    elif normal_count >= MIN_COUNT:
        current_status = NORMAL
    else:
        current_status = previous_status
    if current_status != previous_status:
        device.influenza_monitor_status = current_status

    logger.debug(
        f"{device} case 4: normal={normal_count}, abnormal={warning_count}, "
        f"previous_status {previous_status}, current_status {current_status}"
    )

    if current_status == WARNING and previous_status in (UNKNOWN, NORMAL):
        return DeviceMonitorModel(
            imei=device.imei,
            occurred_at=datetime.utcnow(),
            monitor_case=MONITOR_CASE,
            monitor_status=current_status,
            message=CASE_4_WARNING_TITLE,
            message_detail=CASE_4_WARNING_CONTENT.format(temp=device.temp, humid=device.humid),
        )
    if (current_status == NORMAL and previous_status == WARNING) or (
        current_status == NORMAL and previous_status == UNKNOWN
    ):
        return DeviceMonitorModel(
            imei=device.imei,
            occurred_at=datetime.utcnow(),
            monitor_case=MONITOR_CASE,
            monitor_status=current_status,
            message=CASE_4_NORMAL_TITLE,
            message_detail=CASE_4_NORMAL_CONTENT.format(temp=device.temp, humid=device.humid),
        )
    # logger.debug(f"{device} does not match any conditions")


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

        if len(device_stats) >= MIN_COUNT:
            if device_monitor := check_monitor_case_4(device, device_stats):
                logger.debug(f"Generated {device_monitor}: {device_monitor.to_dict()}")
                device_monitors.append(device_monitor)
            if device.is_modified():
                updated_devices.append(device)
        else:
            logger.debug(f"{device} skip checking (statistics-count < {MIN_COUNT})")

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
                f"Generated {len(device_monitors)} DeviceMonitor models: {device_monitors}"
            )

            upsert_monitor_data(devices, device_monitors)
            logger.info(
                f"Updated {len(devices)} Devices successfully: {devices}, "
                f"Inserted {len(device_monitors)} DeviceMonitors successfully: {device_monitors}"
            )
        except Exception as e:
            batch_item_failures.append(record["messageId"])
            logger.error(f"Failed - {e}")

    close_all_sessions()
    return {"batchItemFailures": batch_item_failures}
