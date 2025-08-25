from datetime import UTC, datetime

from pydantic import BaseModel

from src.modules.master.configs import REPORT_TEMPLATE_FILE
from src.modules.master.models import Event

from .base import Message, SlackClient, render_message


class ProjectStatistic(BaseModel):
    name: str
    total: int
    event_type_stats: dict[str, int]


class ReportContext(BaseModel):
    date: str
    total: int
    projects: list[ProjectStatistic]


class ReportNotifier:
    def __init__(self, client: SlackClient):
        self.client = client

    @staticmethod
    def events_to_message(events: list[Event]) -> Message:
        report_date = datetime.now(UTC).strftime("%Y-%m-%d")

        # Build statistics
        total_events = len(events)
        event_type_stats = {}
        top_events = []
        for event in events:
            event_type = getattr(event, "type", "Unknown")
            event_type_stats[event_type] = event_type_stats.get(event_type, 0) + 1
            # Add top events (customize as needed)
            if len(top_events) < 5:
                top_events.append(
                    {
                        "summary": getattr(event, "summary", str(event)),
                        "type": event_type,
                        "time": getattr(event, "time", ""),
                    }
                )
        context = {
            "color": "#36a64f",
            "report_date": report_date,
            "total_events": total_events,
            "event_type_stats": event_type_stats,
            "top_events": top_events,
        }
        return render_message(REPORT_TEMPLATE_FILE, context)

    def notify(self, events: list[Event]):
        message = self.events_to_message(events)
        self.client.send(message)
