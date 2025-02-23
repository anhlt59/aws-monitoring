from mock import MagicMock

from src.handlers.update_firmware.start_firmware_update import main
from src.services.devices import FirmwareInfo

main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)


def test_update_firmware_success(dummy_device):
    main.device_service.iot.publish = MagicMock(side_effect=lambda *a, **kw: None)
    main.handler({}, None)
    main.device_service.iot.publish.assert_called_once()

    main.device_service.get_firmware_info = MagicMock(
        side_effect=lambda *a, **kw: FirmwareInfo(version="0.0.0", url="")
    )
    main.device_service.iot.publish = MagicMock(side_effect=lambda *a, **kw: None)
    main.handler({}, None)
    main.device_service.iot.publish.assert_not_called()
