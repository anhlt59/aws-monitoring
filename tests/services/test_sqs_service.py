import pytest

from src.constants import SQS_NOTIFICATION_URL
from src.services.sqs import SqsService
from src.types import SqsMessage

sqs_service = SqsService()


def test_send_message():
    message = SqsMessage(message_body="test")

    with pytest.raises(ValueError):
        sqs_service.send_messages(None, [message])  # noqa

    sqs_service.send_messages(SQS_NOTIFICATION_URL, [message])
    messages = sqs_service.client.receive_message(QueueUrl=SQS_NOTIFICATION_URL).get("Messages", [])
    assert len(messages) == 1

    sqs_service.client.purge_queue(QueueUrl=SQS_NOTIFICATION_URL)
