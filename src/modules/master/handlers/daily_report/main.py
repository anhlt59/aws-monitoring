from datetime import datetime, timedelta

from src.common.logger import logger
from src.modules.master.configs import REPORT_WEBHOOK_URL
from src.modules.master.models.event import ListEventsDTO
from src.modules.master.services.db import EventRepository
from src.modules.master.services.notifiers import SlackClient, render_message

# Initialize services
event_repo = EventRepository()
slack_client = SlackClient(REPORT_WEBHOOK_URL)


def send_report(events, report_date=None):
    """
    Build context, render Slack message from report.json, and send it.
    """
    if report_date is None:
        report_date = datetime.now().strftime("%Y-%m-%d")
    # Build statistics
    total_events = len(events.items)
    event_type_stats = {}
    top_events = []
    for event in events.items:
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
    # Render message from template
    message = render_message("statics/templates/report.json", context)
    # Send to Slack
    slack_client.send(message)


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

    # TODO: Push notification to Slack
    #
    logger.info("Daily report sent")
