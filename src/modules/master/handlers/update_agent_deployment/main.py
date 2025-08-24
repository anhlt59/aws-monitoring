from src.common.logger import logger
from src.common.utils.datetime_utils import datetime_str_to_timestamp
from src.infras.aws.data_classes import CfnStackEvent, event_source
from src.modules.master.configs import DEPLOYMENT_WEBHOOK_URL
from src.modules.master.models.agent import Agent, UpdateAgentDTO
from src.modules.master.models.master import Master, UpdateMasterDTO
from src.modules.master.services.db import AgentRepository, MasterRepository
from src.modules.master.services.notifiers import CloudFormationNotifier, SlackClient

notifier = CloudFormationNotifier(
    client=SlackClient(DEPLOYMENT_WEBHOOK_URL),
)
agent_repo = AgentRepository()
master_repo = MasterRepository()


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


def upsert_master(event: CfnStackEvent):
    try:
        if master_repo.exists(event.account):
            master_repo.update(
                event.account,
                UpdateMasterDTO(
                    region=event.region,
                    status=event.stack_data.status,
                    deployed_at=datetime_str_to_timestamp(event.time),
                ),
            )
        else:
            master_repo.create(
                Master(
                    id=event.account,
                    region=event.region,
                    status=event.stack_data.status,
                    deployed_at=datetime_str_to_timestamp(event.time),
                )
            )
    except Exception as e:
        logger.error(f"Failed to upsert master {event.account}: {e}")


@event_source(data_class=CfnStackEvent)
def handler(event: CfnStackEvent, context):
    """Handle the incoming event."""
    logger.debug(event.raw_event)

    if event.source == "aws.cloudformation":
        if event.stack_data.name.startswith("monitoring-master"):
            upsert_master(event)
        else:
            upsert_agent(event)

        notifier.notify(event)
        logger.info(f"Sent Event<{event.get_id}> notification")

    else:
        logger.warning(f"Unsupported event source: {event.source}")
