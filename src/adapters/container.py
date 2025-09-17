from typing import Any, Callable, Dict

from src.adapters.secondary.aws.eventbridge.event_publisher import EventBridgeEventPublisher
from src.adapters.secondary.notifications.slack.notifier import SlackNotifier
from src.adapters.secondary.persistence.dynamodb.agent_repository import DynamoDBAgentRepository
from src.adapters.secondary.persistence.dynamodb.event_repository import DynamoDBEventRepository
from src.application.master.use_cases.generate_daily_report import GenerateDailyReportUseCase
from src.application.master.use_cases.handle_monitoring_event import HandleMonitoringEventUseCase
from src.application.master.use_cases.update_deployment import UpdateDeploymentUseCase


class DIContainer:
    """Dependency Injection Container for Hexagonal Architecture"""

    def __init__(self):
        self._services: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._setup_services()

    def _setup_services(self):
        """Configure all services and their dependencies"""

        # Secondary Adapters (Infrastructure)
        self.register("event_repository", lambda: DynamoDBEventRepository(), singleton=True)
        self.register("agent_repository", lambda: DynamoDBAgentRepository(), singleton=True)
        self.register("notifier", lambda: SlackNotifier(), singleton=True)
        self.register("event_publisher", lambda: EventBridgeEventPublisher(), singleton=True)

        # Use Cases (Application Layer)
        self.register(
            "handle_monitoring_event_use_case",
            lambda: HandleMonitoringEventUseCase(
                event_repository=self.resolve("event_repository"),
                notifier=self.resolve("notifier"),
            ),
        )

        self.register(
            "generate_daily_report_use_case",
            lambda: GenerateDailyReportUseCase(
                event_repository=self.resolve("event_repository"),
                agent_repository=self.resolve("agent_repository"),
                notifier=self.resolve("notifier"),
            ),
        )

        self.register(
            "update_deployment_use_case",
            lambda: UpdateDeploymentUseCase(
                agent_repository=self.resolve("agent_repository"),
                notifier=self.resolve("notifier"),
            ),
        )

    def register(self, name: str, factory: Callable, singleton: bool = False):
        """Register a service with the container"""
        self._services[name] = (factory, singleton)

    def resolve(self, name: str) -> Any:
        """Resolve a service from the container"""
        if name not in self._services:
            raise ValueError(f"Service '{name}' not registered")

        factory, is_singleton = self._services[name]

        if is_singleton:
            if name not in self._singletons:
                self._singletons[name] = factory()
            return self._singletons[name]

        return factory()


# Global container instance
container = DIContainer()
