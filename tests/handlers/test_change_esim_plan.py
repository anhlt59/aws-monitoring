from mock import MagicMock

from src.handlers.change_esim_plan import main
from src.repositories import DeviceRepository

IMEI = "350457796259260"
SIM_ID = "8942310221008800007"

device_repository = DeviceRepository()


def test_normal_case(dummy_device):
    # dummy & mock
    event = {
        "parameter1": SIM_ID,
        "parameter2": "standby",
        "parameter3": "active",
    }
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    main.publish_message_to_device = MagicMock(side_effect=lambda *a, **kw: None)
    main.soracom_service.add_subscription = MagicMock(side_effect=lambda *a, **kw: None)
    # test
    main.handler(event, None)
    device = device_repository.get(IMEI)
    assert device.sim_plan == "planX3"
