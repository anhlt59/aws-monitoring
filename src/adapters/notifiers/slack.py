import requests

from .base import Message, Notifier


class SlackNotifier(Notifier):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def notify(self, message: Message):
        headers = {"Content-Type": "application/json"}
        payload = {
            "text": message.body or "",
            "attachments": message.attachments if message.attachments else [],
        }
        response = requests.post(self.webhook_url, headers=headers, json=payload, timeout=5)
        response.raise_for_status()
