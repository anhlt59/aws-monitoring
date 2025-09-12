from dependency_injector import containers, providers

from src.common.constants import AWS_ENDPOINT, AWS_REGION
from src.infras.aws import CloudwatchLogService, ECSService, EventBridgeService, LambdaService
from src.modules.agent.services import MonitoringService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["src.modules.agent.handlers.query_error_logs.main"],
    )

    cloudwatch_log_service = providers.Factory(CloudwatchLogService, region=AWS_REGION, endpoint_url=AWS_ENDPOINT)
    lambda_service = providers.Factory(LambdaService, region=AWS_REGION, endpoint_url=AWS_ENDPOINT)
    ecs_service = providers.Factory(ECSService, region=AWS_REGION, endpoint_url=AWS_ENDPOINT)
    event_bridge_service = providers.Factory(EventBridgeService, region=AWS_REGION, endpoint_url=AWS_ENDPOINT)

    monitoring_service = providers.Factory(
        MonitoringService,
        cloudwatch_log_service=cloudwatch_log_service,
        lambda_service=lambda_service,
        ecs_service=ecs_service,
        publisher=event_bridge_service,
    )


# Initialize container
container = Container()
