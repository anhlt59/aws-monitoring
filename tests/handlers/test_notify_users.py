import firebase_admin
from mock import MagicMock

from src.repositories import DeviceMonitorRepository, DeviceRepository
from src.services.ses import SesService

device_repository = DeviceRepository()
device_monitor_repository = DeviceMonitorRepository()

IMEI = "350457796259260"


def test_normal_case(
    dummy_device, dummy_alert_setting, dummy_notify_user_device, dummy_device_monitor, dummy_device_token
):
    # mock
    firebase_admin.credentials.Certificate = MagicMock(side_effect=lambda *a, **kw: None)
    firebase_admin.initialize_app = MagicMock(side_effect=lambda *a, **kw: None)

    from src.handlers.notify_users import main
    from src.services.firebase import FirebaseMessagingService

    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    FirebaseMessagingService.send_messages = MagicMock(side_effect=lambda *a, **kw: None)
    SesService.send_emails = MagicMock(side_effect=lambda *a, **kw: None)

    # dummy
    event = {
        "Records": [
            {
                "messageId": "6509b4f2-5869-4245-b4bd-a7a893b040df",
                "body": device_monitor_repository.to_json([dummy_device_monitor]),
            }
        ]
    }
    main.handler(event, None)
