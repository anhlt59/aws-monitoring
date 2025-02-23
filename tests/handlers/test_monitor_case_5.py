from datetime import datetime, timedelta

from mock import MagicMock

from src.handlers.monitors.case_5 import main
from src.repositories import DeviceMonitorRepository, DeviceRepository, StatisticRepository
from src.repositories.sensors import SensorRepository
from src.types import MonitorCases, MonitorStatus

device_repository = DeviceRepository()
device_monitor_repository = DeviceMonitorRepository()
sensor_repository = SensorRepository()
statistic_repository = StatisticRepository()
IMEI = "350457796259260"


def clear():
    device_monitor_repository.delete_all()
    statistic_repository.delete_all()


def test_normal_case(dummy_device, dummy_alert_setting):
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    # dummy
    now = datetime.utcnow()
    statistic_repository.bulk_create([{"imei": dummy_device.imei, "sensor_time": now, "co2_diff": 35}])
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
        dummy_device.imei, MonitorCases.LONG_TERM_ABSENCE
    )
    assert device_monitor.monitor_status == MonitorStatus.NORMAL

    device = device_repository.get(dummy_device.imei)
    assert device.long_absenc_monitor_status == MonitorStatus.NORMAL

    assert not result["batchItemFailures"]
    clear()


def test_abnormal_case(dummy_device, dummy_alert_setting):
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    # dummy
    now = datetime.utcnow()
    statistic_repository.bulk_create(
        [
            {"imei": dummy_device.imei, "sensor_time": now - timedelta(minutes=i * 5), "co2_diff": 5}
            for i in range(0, 24)
        ]
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
        MonitorCases.LONG_TERM_ABSENCE,
    )
    assert device_monitor.monitor_status == MonitorStatus.ABNORMAL

    device = device_repository.get(dummy_device.imei)
    assert device.long_absenc_monitor_status == MonitorStatus.ABNORMAL

    assert not result["batchItemFailures"]
    clear()
