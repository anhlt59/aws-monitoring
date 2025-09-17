from datetime import datetime, timedelta

from dependency_injector.wiring import Provide, inject

from src.common.logger import logger
from src.entrypoints.functions.daily_report.container import Container
from src.infra.db.repositories import EventRepository
from src.modules.master.models.event import ListEventsDTO
from src.modules.master.services.notifiers.report_notifier import ReportInput, ReportNotifier


# @logger.inject_lambda_context(log_event=True)
@inject
def handler(
    event,
    context,
    event_repo: EventRepository = Provide[Container.event_repo],
    notifier: ReportNotifier = Provide[Container.notifier],
) -> None:
    end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=1)

    # Fetch events from the repository
    events = event_repo.list(
        ListEventsDTO(
            start_date=int(start_date.timestamp()),
            end_date=int(end_date.timestamp()),
            limit=100,
        )
    )
    logger.debug(f"Fetched {len(events.items)} events for daily report")

    if events:
        # Send report to Slack
        notifier.report(data=ReportInput(date=start_date.date(), events=events.items))
        logger.info("Daily report sent")


# # Initialize container
# container = Container()
# container.wire(modules=["src.entrypoints.functions.daily_report.main", __name__])
handler(None, None)
