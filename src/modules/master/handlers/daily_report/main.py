from datetime import datetime, timedelta

from src.common.logger import logger
from src.modules.master.configs import REPORT_WEBHOOK_URL
from src.modules.master.models.event import ListEventsDTO
from src.modules.master.services.notifiers import ReportNotifier, SlackClient
from src.modules.master.services.repositories import EventRepository

# Initialize services
event_repo = EventRepository()
notifier = ReportNotifier(
    client=SlackClient(REPORT_WEBHOOK_URL),
)


# @logger.inject_lambda_context(log_event=True)
def handler(event, context):
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)

    # Fetch events from the repository
    events = event_repo.list(
        ListEventsDTO(
            start_date=int(start_date.timestamp()),
            end_date=int(end_date.timestamp()),
            limit=100,
        )
    )
    logger.debug(f"Fetched {len(events.items)} events for daily report")

    # Send report to Slack
    notifier.notify()
    logger.info("Daily report sent")
