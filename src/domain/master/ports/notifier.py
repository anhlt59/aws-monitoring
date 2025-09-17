from typing import Any, Dict, List, Protocol

from ..entities.agent import Agent
from ..entities.event import MonitoringEvent


class Notifier(Protocol):
    """Port for sending notifications"""

    async def notify_event(self, event: MonitoringEvent) -> None:
        """Send notification for a monitoring event"""
        ...

    async def notify_agent_status(self, agent: Agent, message: str) -> None:
        """Send notification about agent status change"""
        ...

    async def notify_daily_report(self, report_data: Dict[str, Any]) -> None:
        """Send daily monitoring report"""
        ...

    async def notify_critical_alert(self, title: str, message: str, events: List[MonitoringEvent]) -> None:
        """Send critical alert with multiple events"""
        ...
