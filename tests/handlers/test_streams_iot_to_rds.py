from mock import MagicMock

from src.handlers.stream_iot_to_rds import main
from src.repositories import DeviceRepository

device_repository = DeviceRepository()


def test_update_firmware_success(dummy_device):
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    # test
    event = {
        "event": 1,
        "version": "0.0.019",
        "topic": "/nb/350457796259260/data",
    }
    main.handler(event, None)
    device = device_repository.get(dummy_device.imei)
    assert device.firmware_version == "0.0.019"


def test_update_firmware_failed(dummy_device):
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    # test
    # CASE: device not found
    event = {
        "event": 1,
        "version": "0.0.019",
        "topic": "/nb/350457796259261/data",
    }
    main.handler(event, None)
    assert device_repository.get(350457796259261) is None

    event = {
        "event": 0,
        "version": "0.0.019",
        "topic": f"/nb/{dummy_device.imei}/data",
    }
    main.handler(event, None)
    device = device_repository.get(dummy_device.imei)
    assert device.firmware_version != "1.0.0"
