from mock import MagicMock

from src.constants import SQS_MONITOR_6_URL
from src.handlers.load_disconnected_devices import main
from src.repositories import DeviceRepository
from src.services.sqs import SqsService
from src.types import DeviceStatus

device_repository = DeviceRepository()
sqs_service = SqsService()
IMEI = "350457796259260"
SIM_ID = "8942310221008800007"
OFFLINE_SIMS = [
    {
        "operatorId": "OP0041303364",
        "simId": SIM_ID,
        "lastModifiedTime": 1690436638075,
        "sessionStatus": {
            "lastUpdatedAt": 1672913385908,
            "imsi": "295050914174001",
            "imei": None,
            "online": False,
            "subscription": "plan01s",
        },
        "previousSession": {
            "imsi": "295050914174001",
            "imei": IMEI,
            "subscription": "plan01s",
        },
    },
]
ONLINE_SIMS = [
    {
        "operatorId": "OP0041303364",
        "simId": SIM_ID,
        "lastModifiedTime": 1690436638075,
        "sessionStatus": {
            "lastUpdatedAt": 1672913385908,
            "imsi": "295050914174001",
            "imei": IMEI,
            "online": True,
            "subscription": "plan01s",
        },
        "previousSession": {
            "imsi": "295050914174001",
            "imei": IMEI,
            "subscription": "plan01s",
        },
    },
]


def clear():
    # clear queue messages
    sqs_service.client.purge_queue(QueueUrl=SQS_MONITOR_6_URL)


def test_offline_case(dummy_abnormal_device):
    # mock
    main.soracom_service.search_sims = MagicMock(side_effect=lambda *a, **kw: OFFLINE_SIMS)
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)

    # test
    main.handler(None, None)

    messages = sqs_service.client.receive_message(QueueUrl=SQS_MONITOR_6_URL).get("Messages", [])
    assert len(messages) == 1

    device = device_repository.get(IMEI)
    assert device.device_status == DeviceStatus.OFFLINE

    clear()


def test_online_case(dummy_abnormal_device):
    # mock
    main.soracom_service.search_sims = MagicMock(side_effect=lambda *a, **kw: ONLINE_SIMS)
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)

    # test
    main.handler(None, None)

    messages = sqs_service.client.receive_message(QueueUrl=SQS_MONITOR_6_URL).get("Messages", [])
    assert len(messages) == 1

    device = device_repository.get(IMEI)
    assert device.device_status == DeviceStatus.ABNORMAL

    clear()


def test_normal_case(dummy_device):
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)

    # test
    main.handler(None, None)
    messages = sqs_service.client.receive_message(QueueUrl=SQS_MONITOR_6_URL).get("Messages", [])
    assert len(messages) == 0

    device = device_repository.get(IMEI)
    assert device.device_status == DeviceStatus.ONLINE


# def test_soracom(dummy_soracom_devices):
#     main.handler(None, None)
#     messages = sqs_service.client.receive_message(QueueUrl=SQS_MONITOR_6_URL).get("Messages", [])
#     assert len(messages) == 1
#     items = json.loads(messages[0]['Body'])
#     assert len(items) == 2
#
#     device = device_repository.get('350457796259263')
#     assert device.device_status == DeviceStatus.OFFLINE
#
#     device = device_repository.get('350457796260360')
#     assert device.device_status == DeviceStatus.ABNORMAL
#
#     device = device_repository.get('350457796260592')
#     assert device.device_status == DeviceStatus.ONLINE
#     clear()
