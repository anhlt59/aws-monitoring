from datetime import UTC, datetime, timedelta

from src.common.logger import logger
from src.domain.models.event import ListEventsDTO
from src.domain.ports import IEventRepository, IReportNotifier


async def daily_report_use_case(event_repo: IEventRepository, notifier: IReportNotifier):
    """Daily report use-case.
    1. Fetch events of previous day from the database.
    2. Generate a report & send the report to the subscribers.
    """
    # 1. Fetch events of previous day from the database.
    end_date = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=1)

    result = await event_repo.list(
        ListEventsDTO(
            start_date=int(start_date.timestamp()),
            end_date=int(end_date.timestamp()),
            limit=100,
        )
    )
    logger.debug(f"Fetched {len(result.items)} events for daily report")

    # 2. Generate a report & send the report to the subscribers.
    await notifier.report(result.items)
