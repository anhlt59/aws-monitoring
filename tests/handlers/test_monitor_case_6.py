from datetime import datetime, timedelta

from mock import MagicMock

from src.handlers.monitors.case_6 import main
from src.repositories import DeviceMonitorRepository, DeviceRepository
from src.services.soracom import SoracomService
from src.types import DeviceStatus, MonitorCases, MonitoringThresholds, MonitorStatus

device_repository = DeviceRepository()
device_monitor_repository = DeviceMonitorRepository()
soracom_service = SoracomService()

IMEI = "350457796259260"
SIM_ID = "8942310221008800007"


def clear():
    device_monitor_repository.delete_all()


def test_offline_case(dummy_abnormal_device):
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    # dummy
    sensor_time = datetime.utcnow() - timedelta(seconds=MonitoringThresholds.APP_NOTIFICATION_DISCONNECT_DURATION + 60)
    device_repository.update(
        dummy_abnormal_device.imei,
        {"sensor_time": sensor_time},
    )
    event = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "body": device_repository.to_json([dummy_abnormal_device]),
                "messageAttributes": {"device_status": {"stringValue": DeviceStatus.OFFLINE}},
            }
        ]
    }
    # test
    result = main.handler(event, None)
    device_monitor = device_monitor_repository.get_last_device_monitor(
        dummy_abnormal_device.imei, MonitorCases.LONG_TERM_DISCONNECT
    )
    assert device_monitor.monitor_status == MonitorStatus.WARNING

    device = device_repository.get(dummy_abnormal_device.imei)
    assert device.long_disconnect_monitor_status == MonitorStatus.WARNING

    assert not result["batchItemFailures"]
    clear()


def test_offline_4day_case(dummy_abnormal_device):
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    # dummy
    device_repository.update(dummy_abnormal_device.imei, {"sensor_time": datetime.utcnow() - timedelta(days=4)})
    event = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "body": device_repository.to_json([dummy_abnormal_device]),
                "messageAttributes": {"device_status": {"stringValue": DeviceStatus.OFFLINE}},
            }
        ]
    }
    # test
    result = main.handler(event, None)
    device_monitor = device_monitor_repository.get_last_device_monitor(
        dummy_abnormal_device.imei, MonitorCases.LONG_TERM_DISCONNECT
    )
    assert device_monitor.monitor_status == MonitorStatus.ABNORMAL

    device = device_repository.get(dummy_abnormal_device.imei)
    assert device.long_disconnect_monitor_status == MonitorStatus.ABNORMAL

    assert not result["batchItemFailures"]
    clear()


def test_online_case(dummy_abnormal_device):
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    # dummy
    device_repository.update(dummy_abnormal_device.imei, {"sensor_time": datetime.utcnow()})
    event = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "body": device_repository.to_json([dummy_abnormal_device]),
                "messageAttributes": {"device_status": {"stringValue": DeviceStatus.ONLINE}},
            }
        ]
    }
    # test
    result = main.handler(event, None)
    device_monitor = device_monitor_repository.get_last_device_monitor(
        dummy_abnormal_device.imei, MonitorCases.LONG_TERM_DISCONNECT
    )
    assert device_monitor.monitor_status == MonitorStatus.NORMAL

    device = device_repository.get(dummy_abnormal_device.imei)
    assert device.long_disconnect_monitor_status == MonitorStatus.NORMAL

    assert not result["batchItemFailures"]
    clear()
