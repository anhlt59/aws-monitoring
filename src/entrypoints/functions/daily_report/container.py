from dependency_injector import containers, providers

from src.infra.db.repositories import EventRepository
from src.modules.master.configs import REPORT_WEBHOOK_URL
from src.modules.master.services.notifiers.report_notifier import ReportNotifier, SlackClient


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["src.entrypoints.functions.daily_report.main", __name__])
    event_repo = providers.Factory(EventRepository)
    slack_client = providers.Factory(SlackClient, webhook_url=REPORT_WEBHOOK_URL)
    notifier = providers.Factory(ReportNotifier, client=slack_client)


# Initialize container
container = Container()
