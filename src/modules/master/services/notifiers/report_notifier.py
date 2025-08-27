from collections import defaultdict
from datetime import date

from pydantic import BaseModel

from src.modules.master.configs import METADATA, REPORT_TEMPLATE_FILE
from src.modules.master.models.event import Event, Severity

from .base import Message, SlackClient, render_message


class ReportInput(BaseModel):
    date: date
    events: list[Event]


class EventCategories(BaseModel):
    critical: list[Event] = []
    high: list[Event] = []
    medium: list[Event] = []
    low: list[Event] = []
    unknown: list[Event] = []


class AccountStatistic(BaseModel):
    id: str
    name: str
    events: EventCategories

    @property
    def total(self) -> int:
        return (
            len(self.events.critical)
            + len(self.events.high)
            + len(self.events.medium)
            + len(self.events.low)
            + len(self.events.unknown)
        )


class ReportNotifier:
    def __init__(self, client: SlackClient):
        self.client = client

    @staticmethod
    def make_report(data: ReportInput) -> Message:
        # Categorize events by account and severity
        events_categories = defaultdict(EventCategories)
        for _id in METADATA:
            events_categories[_id] = EventCategories()

        for event in data.events:
            stats = events_categories[event.account]
            match event.severity:
                case Severity.CRITICAL:
                    stats.critical.append(event)
                case Severity.HIGH:
                    stats.high.append(event)
                case Severity.MEDIUM:
                    stats.medium.append(event)
                case Severity.LOW:
                    stats.low.append(event)
                case _:
                    stats.unknown.append(event)

        # Prepare statistics for rendering
        statistics = [
            AccountStatistic(id=_id, name=METADATA[_id], events=events_categories[_id]) for _id in events_categories
        ]

        context = {
            "color": "#4089a3",
            "date": data.date,
            "total": len(data.events),
            "statistics": statistics,
        }
        return render_message(REPORT_TEMPLATE_FILE, context)

    def report(self, data: ReportInput):
        message = self.make_report(data)
        self.client.send(message)
