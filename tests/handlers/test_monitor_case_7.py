from datetime import datetime, timedelta

from mock import MagicMock

from src.handlers.monitors.case_7 import main
from src.repositories import DeviceMonitorRepository, DeviceRepository, StatisticRepository
from src.repositories.sensors import SensorRepository
from src.types import DeviceState, MonitorCases, MonitoringThresholds, MonitorStatus

device_repository = DeviceRepository()
device_monitor_repository = DeviceMonitorRepository()
sensor_repository = SensorRepository()
statistic_repository = StatisticRepository()

IMEI = "350457796259260"


def clear():
    statistic_repository.delete_all()
    device_monitor_repository.delete_all()


def test_normal_case(dummy_device):
    """co2_diff < MonitoringThresholds.CO2_DIFF => device.intruder_monitor_status wouldn't be updated"""
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    # dummy
    now = datetime.utcnow()
    device_repository.update(
        dummy_device.imei,
        {
            "device_state": DeviceState.ABSENCE,
            "sensor_time": now,
            "intruder_monitor_status": MonitorStatus.NORMAL,
        },
    )
    statistic_repository.create(
        {
            "imei": dummy_device.imei,
            "co2_diff": MonitoringThresholds.CO2_DIFF - 1,
            "sensor_time": datetime.utcnow(),
        }
    )
    event = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "body": device_repository.to_json([dummy_device]),
            }
        ]
    }
    # test
    result = main.handler(event, None)

    device_monitor = device_monitor_repository.get_last_device_monitor(
        dummy_device.imei,
        MonitorCases.SUSPICIOUS_INTRUDER,
    )
    assert device_monitor is None

    device = device_repository.get(dummy_device.imei)
    assert device.intruder_monitor_status == MonitorStatus.NORMAL

    assert not result["batchItemFailures"]
    clear()


def test_abnormal_case(dummy_device):
    """co2_diff >= 35 => update device.intruder_monitor_status=ABNORMAL"""
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    # dummy
    now = datetime.utcnow()
    device_repository.update(
        dummy_device.imei,
        {
            "device_state": DeviceState.ABSENCE,
            "sensor_time": now,
        },
    )
    statistic_repository.create(
        {
            "imei": dummy_device.imei,
            "co2_diff": MonitoringThresholds.CO2_DIFF,
            "sensor_time": datetime.utcnow(),
        }
    )
    event = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "body": device_repository.to_json([dummy_device]),
            }
        ]
    }
    # test
    result = main.handler(event, None)

    device_monitor = device_monitor_repository.get_last_device_monitor(
        dummy_device.imei,
        MonitorCases.SUSPICIOUS_INTRUDER,
    )
    assert device_monitor.monitor_status == MonitorStatus.ABNORMAL

    device = device_repository.get(dummy_device.imei)
    assert device.intruder_monitor_status == MonitorStatus.ABNORMAL

    assert not result["batchItemFailures"]
    clear()


def test_recovery_case(dummy_device):
    """device has been absented more than 4 hours => update device.intruder_monitor_status=NORMAL"""
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    # dummy
    now = datetime.utcnow()
    device_repository.update(
        dummy_device.imei,
        {
            "device_state": DeviceState.ABSENCE,
            "sensor_time": now,
            "intruder_monitor_status": MonitorStatus.ABNORMAL,
        },
    )
    device_monitor_repository.create(
        {
            "imei": dummy_device.imei,
            "monitor_case": MonitorCases.SUSPICIOUS_INTRUDER,
            "occurred_at": now - timedelta(hours=4, minutes=1),
            "monitor_status": MonitorStatus.ABNORMAL,
        }
    )
    statistic_repository.create(
        {
            "imei": dummy_device.imei,
            "co2_diff": MonitoringThresholds.CO2_DIFF - 1,
            "sensor_time": datetime.utcnow(),
        }
    )
    event = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "body": device_repository.to_json([dummy_device]),
            }
        ]
    }
    # test
    result = main.handler(event, None)

    device_monitor = device_monitor_repository.get_last_device_monitor(
        dummy_device.imei,
        MonitorCases.SUSPICIOUS_INTRUDER,
    )
    assert device_monitor.monitor_status == MonitorStatus.ABNORMAL

    device = device_repository.get(dummy_device.imei)
    assert device.intruder_monitor_status == MonitorStatus.NORMAL

    assert not result["batchItemFailures"]
    clear()
