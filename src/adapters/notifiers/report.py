from collections import defaultdict

from src.common.constants import METADATA, REPORT_TEMPLATE_FILE
from src.common.utils.datetime_utils import timestamp_to_date
from src.domain.models import Event

from .base import Message, SlackClient, render_message


class ReportNotifier:
    def __init__(self, client: SlackClient):
        self.client = client

    @staticmethod
    def events_to_report(events: list[Event]) -> Message:
        # Categorize events by account and detail_type
        mapper = defaultdict(lambda: defaultdict(lambda: 0))

        for _id in METADATA:
            mapper[_id] = defaultdict(lambda: 0)

        start = end = events[0].published_at
        for event in events:
            if event.published_at < start:
                start = event.published_at
            if event.published_at > end:
                end = event.published_at

            stats = mapper[event.account]
            stats[event.detail_type] += 1

        statistics = [{"id": _id, "name": METADATA[_id], "statistics": mapper[_id]} for _id in mapper]

        return render_message(
            REPORT_TEMPLATE_FILE,
            context={
                "start": timestamp_to_date(start),
                "end": timestamp_to_date(end),
                "total": len(events),
                "statistics": statistics,
            },
        )

    def report(self, events: list[Event]):
        message = self.events_to_report(events)
        self.client.send(message)
