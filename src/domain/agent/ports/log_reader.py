from datetime import datetime
from typing import List, Optional, Protocol

from ..entities.log_entry import LogEntry


class LogReader(Protocol):
    """Port for reading logs from external systems"""

    async def read_logs(
        self,
        log_group: str,
        start_time: datetime,
        end_time: datetime,
        filter_pattern: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[LogEntry]:
        """Read logs from a log group within time range"""
        ...

    async def read_error_logs(
        self, log_group: str, start_time: datetime, end_time: datetime, limit: Optional[int] = None
    ) -> List[LogEntry]:
        """Read only error-level logs from a log group"""
        ...

    async def search_logs(
        self, log_groups: List[str], query: str, start_time: datetime, end_time: datetime, limit: Optional[int] = None
    ) -> List[LogEntry]:
        """Search logs across multiple log groups"""
        ...
