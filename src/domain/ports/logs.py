from datetime import datetime
from typing import Iterable, Protocol

from src.adapters.logs import CwQueryResult


class ILogService(Protocol):
    def list_monitoring_log_groups_by_tag(self, tag_name: str, tag_value: str) -> Iterable[str]: ...

    def query_logs(
        self,
        log_group_names: list[str],
        query_string: str,
        start_time: datetime,
        end_time: datetime,
        timeout: int = 15,
        delay: int = 1,
    ) -> Iterable[CwQueryResult]: ...
