from typing import Iterable

import boto3

from src.constants import AWS_ENDPOINT, AWS_REGION, MESSAGE_BATCH_SIZE
from src.logger import logger
from src.types import SqsMessage
from src.utils import chunks


class SqsService:
    def __init__(self):
        self.client = boto3.client("sqs", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION)

    def send_messages(self, queue_url: str, messages: Iterable[SqsMessage]):
        if not queue_url:
            raise ValueError("queue_url can't be None")

        for chunk in chunks(messages, MESSAGE_BATCH_SIZE):
            response = self.client.send_message_batch(
                QueueUrl=queue_url,
                Entries=[
                    {"Id": item.id, "MessageBody": item.message_body, "MessageAttributes": item.message_attributes}
                    for item in chunk
                ],
            )

            if failed_items := response.get("Failed"):
                for item in failed_items:
                    logger.error(f"Message<MessageId={item.get('Id')}> [{item.get('Code')}]: {item.get('Message')}")
            logger.info(f"Sent {len(response.get('Successful', []))} messages to Queue<{queue_url}> successfully")
