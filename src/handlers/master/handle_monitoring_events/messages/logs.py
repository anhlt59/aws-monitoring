from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent

from src.adapters.notifiers import Message


def create_logs_message(event: EventBridgeEvent):
    return Message(event)


# def pushNotifySlack(WebHookUrl, Data, Title):
#     print(Data)
#     for item in Data:
#         message = {"attachments": [{"text": "```" + item + "```", "color": "#Be3125", "title": Title}]}
#         notifySlack(WebHookUrl, message)
