from src.adapters.notifiers import SlackNotifier
from src.common.logger import logger


def create_slack_message(event: dict):
    return ""


def push_alarm_notification(event: dict, notifier: SlackNotifier):
    message = create_slack_message(event)
    notifier.notify(message)
    logger.info("Sent alarm notification")
