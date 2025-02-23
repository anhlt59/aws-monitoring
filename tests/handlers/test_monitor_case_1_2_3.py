from datetime import datetime, timedelta

from mock import MagicMock

from src.handlers.monitors.case_1_2_3 import main
from src.repositories import DeviceMonitorRepository, DeviceRepository, StatisticRepository
from src.types import MonitorCases, MonitorStatus

device_repository = DeviceRepository()
device_monitor_repository = DeviceMonitorRepository()
statistic_repository = StatisticRepository()


def clear():
    statistic_repository.delete_all()
    device_monitor_repository.delete_all()


def test_unknown_case(dummy_device):
    """Statistic count < 5 (MIN_COUNT) so monitor_status is UNKNOWN and no device_monitor is created"""
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)

    # dummy
    now = datetime.utcnow()
    device_repository.update(dummy_device.imei, {"co2": 1000})
    event = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "body": device_repository.to_json([dummy_device]),
            }
        ]
    }
    statistic_repository.bulk_create(
        [
            {
                "imei": dummy_device.imei,
                "co2": 1000,
                "temp": 20,
                "sensor_time": now - timedelta(minutes=5),
            }
        ]
    )
    # test
    result = main.handler(event, None)
    device_monitors = list(
        device_monitor_repository.get_last_device_monitors(
            [dummy_device.imei],
            [
                MonitorCases.CO2,
                MonitorCases.TEMPERATURE,
                MonitorCases.HEATSTROKE,
            ],
        )
    )
    assert len(device_monitors) == 0

    device = device_repository.get(dummy_device.imei)
    assert (
        device.co2_monitor_status
        == device.temp_monitor_status
        == device.heat_stroke_monitor_status
        == MonitorStatus.UNKNOWN
    )
    assert not result["batchItemFailures"]

    clear()


def test_normal_case(dummy_device):
    """Normal case: all monitor_status is NORMAL"""
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    # dummy
    now = datetime.utcnow()
    device_repository.update(dummy_device.imei, {"co2": 1000})
    event = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "body": device_repository.to_json([dummy_device]),
            }
        ]
    }
    statistic_repository.bulk_create(
        [
            {
                "imei": dummy_device.imei,
                "co2": 1000 + i,
                "temp": 20,
                "sensor_time": now - timedelta(minutes=i * 5),
            }
            for i in range(6)
        ]
    )
    # test
    result = main.handler(event, None)
    device_monitors = list(
        device_monitor_repository.get_last_device_monitors(
            [dummy_device.imei],
            [
                MonitorCases.CO2,
                MonitorCases.TEMPERATURE,
                MonitorCases.HEATSTROKE,
            ],
        )
    )
    assert (
        len(device_monitors) == 3
        and device_monitors[0].monitor_status == MonitorStatus.NORMAL
        and device_monitors[1].monitor_status == MonitorStatus.NORMAL
        and device_monitors[2].monitor_status == MonitorStatus.NORMAL
    )

    device = device_repository.get(dummy_device.imei)
    assert (
        device.co2_monitor_status
        == device.temp_monitor_status
        == device.heat_stroke_monitor_status
        == MonitorStatus.NORMAL
    )

    assert not result["batchItemFailures"]
    clear()


def test_warning_case(dummy_device):
    """Warning case 2: co2_monitor_status is WARNING"""
    # mock
    # base.close_session = MagicMock(side_effect=lambda *a, **kw: None)
    # dummy
    now = datetime.utcnow()
    device_repository.update(dummy_device.imei, {"co2": 1500})
    event = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "body": device_repository.to_json([dummy_device]),
            }
        ]
    }
    statistic_repository.bulk_create(
        [
            {
                "imei": dummy_device.imei,
                "co2": 1500 + i,
                "temp": 20,
                "sensor_time": now - timedelta(minutes=i * 5),
            }
            for i in range(6)
        ]
    )
    result = main.handler(event, None)
    device_monitor = device_monitor_repository.get_last_device_monitor(dummy_device.imei, MonitorCases.CO2)
    assert device_monitor.monitor_status == MonitorStatus.WARNING

    device = device_repository.get(dummy_device.imei)
    assert device.co2_monitor_status == MonitorStatus.WARNING

    assert not result["batchItemFailures"]
    clear()


def test_abnormal_case(dummy_device):
    """Abnormal case: all monitor_status is ABNORMAL"""
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    # dummy
    now = datetime.utcnow()
    device_repository.update(dummy_device.imei, {"co2": 5000, "temp": 50})
    event = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "body": device_repository.to_json([dummy_device]),
            }
        ]
    }
    statistic_repository.bulk_create(
        [
            {
                "imei": dummy_device.imei,
                "co2": 5000 + i * 100,
                "temp": 50 + i,
                "sensor_time": now - timedelta(minutes=i * 5),
            }
            for i in range(6)
        ]
    )
    # test
    result = main.handler(event, None)
    device_monitors = list(
        device_monitor_repository.get_last_device_monitors(
            [dummy_device.imei],
            [
                MonitorCases.CO2,
                MonitorCases.TEMPERATURE,
                MonitorCases.HEATSTROKE,
            ],
        )
    )
    assert (
        len(device_monitors) == 3
        and device_monitors[0].monitor_status == MonitorStatus.ABNORMAL
        and device_monitors[1].monitor_status == MonitorStatus.ABNORMAL
        and device_monitors[2].monitor_status == MonitorStatus.ABNORMAL
    )

    device = device_repository.get(dummy_device.imei)
    assert (
        device.co2_monitor_status
        == device.temp_monitor_status
        == device.heat_stroke_monitor_status
        == MonitorStatus.ABNORMAL
    )

    assert not result["batchItemFailures"]
    clear()
