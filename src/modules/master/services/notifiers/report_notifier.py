from collections import defaultdict
from datetime import date

from pydantic import BaseModel

from src.modules.master.configs import METADATA, REPORT_TEMPLATE_FILE
from src.modules.master.models.event import Event

from .base import Message, SlackClient, render_message


class ReportInput(BaseModel):
    date: date
    events: list[Event]


class AccountStatistic(BaseModel):
    id: str
    name: str
    statistics: dict[str, int] = {}

    @property
    def total(self) -> int:
        return sum(self.statistics.values())


class ReportNotifier:
    def __init__(self, client: SlackClient):
        self.client = client

    @staticmethod
    def make_report(data: ReportInput) -> Message:
        # Categorize events by account and detail_type
        mapper = defaultdict(lambda: defaultdict(lambda: 0))

        for _id in METADATA:
            mapper[_id] = defaultdict(lambda: 0)

        for event in data.events:
            stats = mapper[event.account]
            stats[event.detail_type] += 1

        statistics = [AccountStatistic(id=_id, name=METADATA[_id], statistics=mapper[_id]) for _id in mapper]
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
