from datetime import datetime, timedelta

from mock import MagicMock

from src.handlers.monitors.case_4 import main
from src.repositories import DeviceMonitorRepository, DeviceRepository, StatisticRepository
from src.repositories.sensors import SensorRepository
from src.services.soracom import SoracomService
from src.types import MonitorCases, MonitorStatus

device_repository = DeviceRepository()
device_monitor_repository = DeviceMonitorRepository()
sensor_repository = SensorRepository()
soracom_service = SoracomService()
statistic_repository = StatisticRepository()

IMEI = "350457796259260"


def clear():
    device_monitor_repository.delete_all()
    statistic_repository.delete_all()


def test_unknown_case(dummy_device):
    """Statistic count < 5 (MIN_COUNT) so monitor_status is UNKNOWN and no device_monitor is created"""
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    # dummy
    now = datetime.utcnow()
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
                "humid": 50,
                "temp": 20,
                "sensor_time": now - timedelta(minutes=5),
            }
        ]
    )
    # test
    result = main.handler(event, None)
    device_monitor = device_monitor_repository.get_last_device_monitor(
        dummy_device.imei,
        MonitorCases.INFLUENZA,
    )
    assert device_monitor is None

    device = device_repository.get(dummy_device.imei)
    assert device.influenza_monitor_status == MonitorStatus.UNKNOWN

    assert not result["batchItemFailures"]
    clear()


def test_normal_case(dummy_device):
    """Normal case: influenza_monitor_status is NORMAL"""
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    # dummy
    now = datetime.utcnow()
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
                "humid": 50 + i,
                "temp": 20 + i,
                "sensor_time": now - timedelta(minutes=i * 5),
            }
            for i in range(6)
        ]
    )
    # test
    result = main.handler(event, None)
    device_monitor = device_monitor_repository.get_last_device_monitor(
        dummy_device.imei,
        MonitorCases.INFLUENZA,
    )
    assert device_monitor.monitor_status == MonitorStatus.NORMAL

    device = device_repository.get(dummy_device.imei)
    assert device.influenza_monitor_status == MonitorStatus.NORMAL

    assert not result["batchItemFailures"]
    clear()


def test_warning_case(dummy_device):
    """Warning case: influenza_monitor_status is WARNING"""
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    # dummy
    now = datetime.utcnow()
    device_repository.update(dummy_device.imei, {"temp": 17, "humid": 39})
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
                "humid": 40 - i,
                "temp": 18 - i,
                "sensor_time": now - timedelta(minutes=i * 5),
            }
            for i in range(1, 6)
        ]
    )
    # test
    result = main.handler(event, None)
    device_monitor = device_monitor_repository.get_last_device_monitor(
        dummy_device.imei,
        MonitorCases.INFLUENZA,
    )
    assert device_monitor.monitor_status == MonitorStatus.WARNING

    device = device_repository.get(dummy_device.imei)
    assert device.influenza_monitor_status == MonitorStatus.WARNING

    assert not result["batchItemFailures"]
    clear()
