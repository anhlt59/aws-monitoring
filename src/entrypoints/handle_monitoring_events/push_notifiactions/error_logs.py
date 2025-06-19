from src.adapters.notifiers import SlackNotifier
from src.common.logger import logger


def create_slack_message(event: dict):
    return ""


def push_error_log_notification(event: dict, notifier: SlackNotifier):
    message = create_slack_message(event)
    notifier.notify(message)
    logger.info("Sent error log notification")
