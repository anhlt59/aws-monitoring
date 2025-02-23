from mock import MagicMock

from src.handlers.update_firmware.confirm_firmware_update import main
from src.repositories import DeviceRepository

device_repository = DeviceRepository()
main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)


def test_firmware_updated_success(dummy_device):
    # test
    event = {
        "event": 2,
        "topic": f"/nb/{dummy_device.imei}/data",
    }
    main.handler(event, None)
