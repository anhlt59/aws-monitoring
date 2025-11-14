from typing import Protocol

from src.domain.models.messages import Message


class IPublisher(Protocol):
    async def publish(self, messages: list[Message]) -> None: ...
