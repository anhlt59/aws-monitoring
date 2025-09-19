from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent

from src.common.logger import logger
from src.common.utils.datetime_utils import datetime_str_to_timestamp
from src.domain.models.agent import Agent, UpdateAgentDTO
from src.domain.ports import IAgentRepository, IEventNotifier
from src.infra.data_classes import CfnStackEvent


def update_deployment_use_case(event: EventBridgeEvent, agent_repo: IAgentRepository, notifier: IEventNotifier):
    """Update deployment use-case.
    1. Insert/Update the agent information in the database.
    2. Notify the event to the subscribers.
    """
    if event.source != "aws.cloudformation":
        raise ValueError(f"Unsupported event source: {event.source}")

    event = CfnStackEvent(event)

    # 1. Insert/Update the agent information in the database.
    if agent_repo.exists(event.account):
        agent_repo.update(
            event.account,
            UpdateAgentDTO(
                region=event.region,
                status=event.stack_data.status,
                deployed_at=datetime_str_to_timestamp(event.time),
            ),
        )
    else:
        agent_repo.create(
            Agent(
                id=event.account,
                region=event.region,
                status=event.stack_data.status,
                deployed_at=datetime_str_to_timestamp(event.time),
            )
        )
    logger.info(f"Upserted Agent<{event.account}> successfully")

    # 2. Notify the event to the subscribers.
    notifier.notify(event)
    logger.info(f"Sent Event<{event.get_id}> successfully")
