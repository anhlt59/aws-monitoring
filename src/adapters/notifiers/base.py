from typing import Any, Protocol

from pydantic import BaseModel


class Message(BaseModel):
    body: str | None = None
    attachments: list[Any] | None = None


class Notifier(Protocol):
    def notify(self, message: Message): ...
