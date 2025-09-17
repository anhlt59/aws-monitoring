from typing import Any, Dict, List, Protocol

from ..entities.log_entry import LogEntry


class EventPublisher(Protocol):
    """Port for publishing events from agent to master"""

    async def publish_log_event(self, log_entry: LogEntry, additional_metadata: Dict[str, Any] = None) -> None:
        """Publish a log entry as a monitoring event"""
        ...

    async def publish_batch_log_events(
        self, log_entries: List[LogEntry], additional_metadata: Dict[str, Any] = None
    ) -> None:
        """Publish multiple log entries as monitoring events"""
        ...

    async def publish_agent_heartbeat(
        self, account: str, region: str, status: str, metadata: Dict[str, Any] = None
    ) -> None:
        """Publish agent heartbeat event"""
        ...
