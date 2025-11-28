"""Get events statistics use case."""

from collections import defaultdict
from pydantic import Field

from src.adapters.db.repositories.event import EventRepository
from src.common.models import BaseModel


class EventsStatsDTO(BaseModel):
    """Events statistics response."""

    total: int = Field(..., description="Total number of events")
    by_severity: dict[str, int] = Field(..., description="Count by severity level")
    by_account: dict[str, int] = Field(..., description="Count by AWS account")
    by_region: dict[str, int] = Field(..., description="Count by AWS region")
    by_source: dict[str, int] = Field(..., description="Count by event source")


class GetEventsStats:
    """
    Use case for retrieving events statistics.

    Aggregates event data by severity, account, region, and source.
    """

    # Severity mapping
    SEVERITY_LABELS = {
        0: "info",
        1: "low",
        2: "medium",
        3: "high",
        4: "critical",
        5: "critical",
    }

    def __init__(self, event_repository: EventRepository | None = None):
        """
        Initialize use case.

        Args:
            event_repository: Event repository instance
        """
        self.event_repository = event_repository or EventRepository()

    def execute(self, start_date: int | None = None, end_date: int | None = None) -> EventsStatsDTO:
        """
        Get events statistics.

        Args:
            start_date: Filter events after this date (Unix timestamp)
            end_date: Filter events before this date (Unix timestamp)

        Returns:
            EventsStatsDTO with aggregated statistics
        """
        # Get events (with date filters if provided)
        from src.domain.models.event import ListEventsDTO

        dto = ListEventsDTO(
            start_date=start_date,
            end_date=end_date,
            limit=10000,  # Large limit to get all events
            direction="desc",
        )
        result = self.event_repository.list(dto)
        events = result.items

        # Initialize counters
        by_severity = defaultdict(int)
        by_account = defaultdict(int)
        by_region = defaultdict(int)
        by_source = defaultdict(int)

        # Aggregate statistics
        for event in events:
            severity_label = self.SEVERITY_LABELS.get(event.severity, "unknown")
            by_severity[severity_label] += 1
            by_account[event.account] += 1
            by_region[event.region] += 1
            by_source[event.source] += 1

        return EventsStatsDTO(
            total=len(events),
            by_severity=dict(by_severity),
            by_account=dict(by_account),
            by_region=dict(by_region),
            by_source=dict(by_source),
        )
