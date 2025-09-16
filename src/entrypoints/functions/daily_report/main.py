from datetime import datetime, timedelta

from src.common.logger import logger
from src.infra.db.repositories import EventRepository
from src.modules.master.configs import REPORT_WEBHOOK_URL
from src.modules.master.models.event import ListEventsDTO
from src.modules.master.services.notifiers.report_notifier import ReportInput, ReportNotifier, SlackClient

# Initialize services
event_repo = EventRepository()
notifier = ReportNotifier(
    client=SlackClient(REPORT_WEBHOOK_URL),
)


# @logger.inject_lambda_context(log_event=True)
def handler(event, context):
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
