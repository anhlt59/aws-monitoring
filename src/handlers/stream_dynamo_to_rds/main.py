import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from functools import reduce

from sqlalchemy.orm import close_all_sessions

from src.constants import (
    SQS_MONITOR_4_URL,
    SQS_MONITOR_5_URL,
    SQS_MONITOR_6_URL,
    SQS_MONITOR_7_URL,
    SQS_MONITOR_123_URL,
)
from src.logger import logger
from src.models import DeviceModel, StatisticModel
from src.models.sensors import SensorModel
from src.repositories import DeviceRepository, StatisticRepository
from src.repositories.sensors import SensorRepository
from src.services.sqs import SqsService
from src.types import DeviceState, DeviceStatus, MonitoringThresholds, MonitorStatus

TRACKING_OFFSET = -23  # minutes
TRACKING_DURATION = 5  # minutes

executor = ThreadPoolExecutor(max_workers=8)
device_repository = DeviceRepository()
statistic_repository = StatisticRepository()
sensor_repository = SensorRepository()
sqs_service = SqsService()


def prepare_models_for_upsertion(
    devices: list[DeviceModel], sensors: list[SensorModel]
) -> (list[DeviceModel], list[StatisticModel]):
    now = datetime.utcnow()
    sensor_mapping: dict[str:SensorModel] = {}
    # dummy min_sensor_time and max_sensor_time
    min_sensor_time = max_sensor_time = sensors[0].sensor_time

    for sensor in sensors:
        # If 2 or more sensor data with the same IMEI, then only the latest one will be used.
        if sensor_mapping.get(sensor.IMEI) and sensor.sensor_time <= sensor_mapping[sensor.IMEI].sensor_time:
            # The rest will be ignored.
            continue

        # mapping sensor by imei
        sensor_mapping[sensor.IMEI] = sensor
        # update min_sensor_time and max_sensor_time
        if sensor.sensor_time < min_sensor_time:
            min_sensor_time = sensor.sensor_time
        if sensor.sensor_time > max_sensor_time:
            max_sensor_time = sensor.sensor_time

    # get statistic items that have sensor_time between (18 minutes ago, 23 minutes ago)
    statistics_groups = statistic_repository.group_statistics_by_imei(
        imeis=sensor_mapping.keys(),
        since=min_sensor_time + timedelta(minutes=TRACKING_OFFSET),
        until=max_sensor_time + timedelta(minutes=TRACKING_OFFSET + TRACKING_DURATION),
    )
    logger.debug(f"statistics 18-23 minutes ago: {statistics_groups}")
    # then mapping statistic by imei
    stats_mapping: dict[str : StatisticModel | None] = {}
    for imei, stats in statistics_groups.items():
        if sensor := sensor_mapping.get(imei):
            left_offset = sensor.sensor_time + timedelta(minutes=TRACKING_OFFSET)
            right_offset = sensor.sensor_time + timedelta(minutes=TRACKING_OFFSET + TRACKING_DURATION)
            # get the latest statistic item that has sensor_time between (18 minutes ago, 23 minutes ago)
            filtered_stats = filter(lambda s: left_offset <= s.sensor_time <= right_offset, stats)
            stats_mapping[imei] = reduce(
                lambda x, y: x if x is not None and x.sensor_time <= y.sensor_time else y, filtered_stats, None
            )

    statistics = []
    updated_devices = []
    for device in devices:
        sensor = sensor_mapping.get(device.imei)
        if sensor and device.sensor_time is None or sensor.sensor_time >= device.sensor_time:
            if (
                device.device_status != DeviceStatus.ONLINE
                and (now - sensor.sensor_time).total_seconds() < MonitoringThresholds.RECOVERY_CONNECTION_DURATION
            ):
                # If device_status is not ONLINE and that device got sensor data for 10 minutes,
                # then change device_status = DeviceStatus.ONLINE
                device.device_status = DeviceStatus.ONLINE
            device.co2 = sensor.co2
            device.temp = sensor.tem
            device.humid = sensor.hum
            device.sensor_time = sensor.sensor_time

            # create statistic model
            statistic = StatisticModel(
                imei=device.imei,
                sensor_time=sensor.sensor_time,
                co2=sensor.co2,
                temp=sensor.tem,
                humid=sensor.hum,
            )
            # calculate co2_diff by subtracting the current CO2 from the CO2 20 minutes ago
            if stats_20mins_ago := stats_mapping.get(device.imei):
                statistic.co2_diff = statistic.co2 - stats_20mins_ago.co2

            statistics.append(statistic)
            updated_devices.append(device)
        else:
            logger.warning(
                f"{device} ignore {sensor} cause invalid sensor_time ({sensor.sensor_time} < {device.sensor_time})"
            )
    return updated_devices, statistics


def upsert_data(devices: list[DeviceModel], statistics: list[StatisticModel]):
    if devices:
        device_repository.bulk_update(models=devices)
    else:
        logger.debug("No Device to insert")

    if statistics:
        statistic_repository.bulk_create(models=statistics, return_defaults=True)
    else:
        logger.debug("No Statistic to insert")


def send_messages(devices: list[DeviceModel]):
    monitoring_devices = disconnected_devices = absented_devices = []
    for device in devices:
        if device.deleted_at is None:
            if device.long_disconnect_monitor_status != MonitorStatus.NORMAL:
                disconnected_devices.append(device)
            if device.device_state == DeviceState.ABSENCE:
                absented_devices.append(device)
            monitoring_devices.append(device)
    logger.debug(
        f"Got {len(monitoring_devices)} monitoring_devices, "
        f"{len(disconnected_devices)} disconnected_devices, "
        f"{len(absented_devices)} absented_devices"
    )

    # prepare sqs messages
    common_messages = list(device_repository.to_sqs_messages(monitoring_devices))
    disconnected_messages = device_repository.to_sqs_messages(
        disconnected_devices,
        message_attributes={"device_status": {"DataType": "Number", "StringValue": str(DeviceStatus.ONLINE)}},
    )
    absented_messages = device_repository.to_sqs_messages(absented_devices)

    # send messages to sqs queues
    tasks = [
        executor.submit(sqs_service.send_messages, SQS_MONITOR_123_URL, common_messages),
        executor.submit(sqs_service.send_messages, SQS_MONITOR_4_URL, common_messages),
        executor.submit(sqs_service.send_messages, SQS_MONITOR_5_URL, common_messages),
        executor.submit(sqs_service.send_messages, SQS_MONITOR_6_URL, disconnected_messages),
        executor.submit(sqs_service.send_messages, SQS_MONITOR_7_URL, absented_messages),
    ]
    # Wait for tasks to be finished
    concurrent.futures.wait(tasks, return_when=concurrent.futures.ALL_COMPLETED)


def handler(event, context):
    records = event.get("Records", [])
    logger.info(f"Got {len(records)} DynamoDB records")

    try:
        # deserialize event.Records
        sensors = list(sensor_repository.deserialize_dynamo_records(records))
        logger.info(f"Got {len(sensors)} Sensors: {sensors}")

        if sensors:
            # get devices by imei
            devices = device_repository.list_devices_by_imei(sensor.IMEI for sensor in sensors)
            logger.info(f"Found {len(devices)} devices: {devices}")

            updated_devices, statistics = prepare_models_for_upsertion(devices, sensors)
            logger.info(
                f"Updated {len(updated_devices)} Device models: {updated_devices}, "
                f"Created {len(statistics)} Statistic models: {statistics}"
            )

            # upsert data to rds
            upsert_data(devices=updated_devices, statistics=statistics)
            logger.info(
                f"Bulk update {len(updated_devices)} devices successfully: {updated_devices}, "
                f"Bulk insert {len(statistics)} statistics successfully: {statistics}"
            )

            # send sqs message to MonitorQueues
            send_messages(devices)
    except Exception as e:
        logger.error(f"`update_devices` failed: {e}")

    close_all_sessions()
