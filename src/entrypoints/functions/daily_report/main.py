from src.adapters.db.repositories import EventRepository
from src.adapters.notifiers import ReportNotifier, SlackClient
from src.common.constants import REPORT_WEBHOOK_URL
from src.common.logger import logger
from src.domain.use_cases.daily_report import daily_report_use_case

event_repo = EventRepository()
notifier = ReportNotifier(client=SlackClient(REPORT_WEBHOOK_URL))


# @logger.inject_lambda_context(log_event=True)
def handler(event, context) -> None:
    try:
        daily_report_use_case(event_repo, notifier)
    except Exception as e:
        logger.error(f"Error occurred while generating daily report: {e}")
