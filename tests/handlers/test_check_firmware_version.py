import json

from mock import MagicMock

from src.handlers.update_firmware.check_firmware_version import main
from src.services.devices import FirmwareInfo

main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)


def test_check_firmware_version(dummy_device):
    main.device_service.iot.publish = MagicMock(side_effect=lambda *a, **kw: None)
    main.handler({}, None)
    main.device_service.iot.publish.assert_called_once_with(
        topic=f"/nb/{dummy_device.imei}/notify", payload=json.dumps({"event": 1})
    )

    main.device_service.get_firmware_info = MagicMock(
        side_effect=lambda *a, **kw: FirmwareInfo(version="0.0.0", url="")
    )
    main.device_service.iot.publish = MagicMock(side_effect=lambda *a, **kw: None)
    main.handler({}, None)
    main.device_service.iot.publish.assert_not_called()
