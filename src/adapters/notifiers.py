from typing import Any, Protocol

import requests
from pydantic import BaseModel


# Interfaces
class Message(BaseModel):
    body: str | None = None
    attachments: list[Any] | None = None


class Notifier(Protocol):
    def notify(self, message: Message): ...


# Slack Notifier Implementation
class SlackNotifier(Notifier):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def notify(self, message: Message):
        headers = {"Content-Type": "application/json"}
        payload = {
            "text": message.body or "",
            "attachments": message.attachments if message.attachments else [],
        }
        response = requests.post(self.webhook_url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
