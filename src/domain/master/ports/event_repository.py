from datetime import datetime
from typing import List, Optional, Protocol

from ..entities.event import MonitoringEvent


class EventRepository(Protocol):
    """Port for event persistence operations"""

    async def save(self, event: MonitoringEvent) -> None:
        """Save an event to the repository"""
        ...

    async def find_by_id(self, event_id: str) -> Optional[MonitoringEvent]:
        """Find an event by its ID"""
        ...

    async def find_by_time_range(
        self, start_time: datetime, end_time: datetime, limit: Optional[int] = None
    ) -> List[MonitoringEvent]:
        """Find events within a time range"""
        ...

    async def find_by_account(self, account: str, limit: Optional[int] = None) -> List[MonitoringEvent]:
        """Find events by account"""
        ...

    async def find_critical_events(self, since: datetime, limit: Optional[int] = None) -> List[MonitoringEvent]:
        """Find critical events since a given time"""
        ...

    async def count_by_time_range(self, start_time: datetime, end_time: datetime) -> int:
        """Count events within a time range"""
        ...

    async def delete_expired_events(self, before: datetime) -> int:
        """Delete events older than specified date, returns count deleted"""
        ...
