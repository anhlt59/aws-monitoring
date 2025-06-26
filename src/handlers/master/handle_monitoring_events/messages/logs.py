from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent

from src.adapters.notifiers import Message


def create_logs_message(event: EventBridgeEvent):
    return Message(event)
