from src.common.logger import logger
from src.common.utils.datetime_utils import datetime_str_to_timestamp
from src.infra.aws.data_classes import CfnStackEvent, event_source
from src.infra.db.repositories import AgentRepository
from src.modules.master.configs import DEPLOYMENT_WEBHOOK_URL
from src.modules.master.models.agent import Agent, UpdateAgentDTO
from src.modules.master.services.notifiers import CloudFormationNotifier, SlackClient

notifier = CloudFormationNotifier(
    client=SlackClient(DEPLOYMENT_WEBHOOK_URL),
)
agent_repo = AgentRepository()


def upsert_agent(event: CfnStackEvent):
    try:
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
    except Exception as e:
        logger.error(f"Failed to upsert agent {event.account}: {e}")


@event_source(data_class=CfnStackEvent)
def handler(event: CfnStackEvent, context):
    """Handle the incoming event."""
    logger.debug(event.raw_event)

    if event.source == "aws.cloudformation":
        upsert_agent(event)
        notifier.notify(event)
        logger.info(f"Sent Event<{event.get_id}> successfully")
    else:
        logger.warning(f"Unsupported event source: {event.source}")
