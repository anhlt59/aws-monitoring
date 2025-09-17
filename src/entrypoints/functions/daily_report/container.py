from dependency_injector import containers, providers

from src.adapters.secondary.aws.eventbridge.event_publisher import EventBridgeEventPublisher
from src.adapters.secondary.notifications.slack.notifier import SlackNotifier
from src.adapters.secondary.persistence.dynamodb.agent_repository import DynamoDBAgentRepository
from src.adapters.secondary.persistence.dynamodb.event_repository import DynamoDBEventRepository
from src.application.master.use_cases.generate_daily_report import GenerateDailyReportUseCase
from src.application.master.use_cases.handle_monitoring_event import HandleMonitoringEventUseCase
from src.application.master.use_cases.update_deployment import UpdateDeploymentUseCase


class Container(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()

    # Secondary Adapters (Infrastructure) - Singletons
    event_repository = providers.Singleton(
        DynamoDBEventRepository,
        table_name=config.dynamodb.table_name.as_(str, default=None)
    )

    agent_repository = providers.Singleton(
        DynamoDBAgentRepository,
        table_name=config.dynamodb.table_name.as_(str, default=None)
    )

    notifier = providers.Singleton(
        SlackNotifier,
        webhook_url=config.slack.webhook_url.as_(str, default=None)
    )

    event_publisher = providers.Singleton(
        EventBridgeEventPublisher,
        event_bus_name=config.eventbridge.bus_name.as_(str, default=None)
    )

    # Use Cases (Application Layer) - Factory providers for fresh instances per request
    handle_monitoring_event_use_case = providers.Factory(
        HandleMonitoringEventUseCase,
        event_repository=event_repository,
        notifier=notifier,
    )

    generate_daily_report_use_case = providers.Factory(
        GenerateDailyReportUseCase,
        event_repository=event_repository,
        agent_repository=agent_repository,
        notifier=notifier,
    )

    update_deployment_use_case = providers.Factory(
        UpdateDeploymentUseCase,
        agent_repository=agent_repository,
        notifier=notifier,
    )


# Global container instance
container = Container()
container.wire(modules=[__name__])
