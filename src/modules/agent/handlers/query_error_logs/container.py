from dependency_injector import containers, providers

from src.common.constants import AWS_ENDPOINT, AWS_REGION
from src.infras.aws import CloudwatchLogService, ECSService, EventBridgeService, LambdaService
from src.modules.agent.services.cloudwatch import CloudwatchService
from src.modules.agent.services.publisher import Publisher


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["src.modules.agent.handlers.query_error_logs.main"],
    )

    cloudwatch_log_service = providers.Singleton(CloudwatchLogService, region=AWS_REGION, endpoint_url=AWS_ENDPOINT)
    lambda_service = providers.Singleton(LambdaService, region=AWS_REGION, endpoint_url=AWS_ENDPOINT)
    ecs_service = providers.Singleton(ECSService, region=AWS_REGION, endpoint_url=AWS_ENDPOINT)
    event_bridge_service = providers.Singleton(EventBridgeService, region=AWS_REGION, endpoint_url=AWS_ENDPOINT)

    cloudwatch_service = providers.Singleton(
        CloudwatchService,
        cloudwatch_log_service=cloudwatch_log_service,
        lambda_service=lambda_service,
        ecs_service=ecs_service,
    )
    publisher = providers.Singleton(Publisher, client=event_bridge_service)
