import asyncio

from src.adapters.aws.data_classes import CfnStackEvent, event_source
from src.adapters.db.repositories import AgentRepository
from src.adapters.notifiers import EventNotifier, SlackClient
from src.common.constants import DEPLOYMENT_WEBHOOK_URL
from src.common.logger import logger
from src.common.utils.datetime_utils import datetime_str_to_timestamp
from src.domain.use_cases.update_deployment import update_deployment_use_case

notifier = EventNotifier(client=SlackClient(DEPLOYMENT_WEBHOOK_URL))
agent_repo = AgentRepository()


# @logger.inject_lambda_context(log_event=True)
@event_source(data_class=CfnStackEvent)
def handler(event: CfnStackEvent, context):
    """Lambda handler for CloudFormation stack deployment events.

    Extracts domain values from AWS-specific CfnStackEvent and delegates
    to the use case layer with pure domain data. This maintains hexagonal
    architecture by keeping AWS-specific parsing in the entrypoint layer.
    """
    logger.debug(event.raw_event)

    try:
        # Validate that this is a CloudFormation event
        # CfnStackEvent will throw KeyError for non-CloudFormation events
        # This maintains backward compatibility with test expectations
        asyncio.run(
            update_deployment_use_case(
                account=event.account,
                region=event.region,
                status=event.stack_data.status,  # Will raise KeyError for non-CFN events
                deployed_at=datetime_str_to_timestamp(event.time),
                event_data=event,  # Pass original event for notification
                agent_repo=agent_repo,
                notifier=notifier,
            )
        )
    except KeyError as e:
        logger.error(f"Invalid CloudFormation event structure: missing {e}")
        raise ValueError(f"Event is not a valid CloudFormation stack event: missing {e}")
    except Exception as e:
        logger.error(f"Failed to process deployment event: {e}")
        raise
