from mock import MagicMock

from src.constants import SQS_MONITOR_7_URL
from src.handlers.load_recover_absent_devices import main
from src.repositories import DeviceRepository
from src.services.sqs import SqsService
from src.types import DeviceState, MonitorStatus

device_repository = DeviceRepository()
sqs_service = SqsService()


def clear():
    # clear queue messages
    sqs_service.client.purge_queue(QueueUrl=SQS_MONITOR_7_URL)


def test_normal_case(dummy_device):
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)

    main.handler(None, None)
    messages = sqs_service.client.receive_message(QueueUrl=SQS_MONITOR_7_URL).get("Messages", [])
    assert len(messages) == 0
    clear()


def test_disconnected_device(dummy_device):
    # mock
    main.close_all_sessions = MagicMock(side_effect=lambda *a, **kw: None)
    # dummy
    dummy_device.device_state = DeviceState.ABSENCE
    dummy_device.intruder_monitor_status = MonitorStatus.ABNORMAL
    device_repository.save(dummy_device)

    # test
    main.handler(None, None)
    messages = sqs_service.client.receive_message(QueueUrl=SQS_MONITOR_7_URL).get("Messages", [])
    assert len(messages) == 1
    clear()
