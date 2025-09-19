from typing import Protocol

from src.adapters.publisher import Message


class IPublisher(Protocol):
    def publish(self, messages: list[Message]) -> None: ...
