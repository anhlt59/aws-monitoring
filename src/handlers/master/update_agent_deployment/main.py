import os

from src.adapters.aws.cloudformation import CfnStackStatus
from src.adapters.aws.data_classes import CfnStackEvent, event_source
from src.adapters.db import AgentRepository
from src.adapters.notifiers import SlackNotifier, render_message
from src.common.exceptions.http import NotFoundError
from src.common.logger import logger
from src.common.utils.datetime_utils import datetime_str_to_timestamp
from src.models.agent import Agent, UpdateAgentDTO

TEMPLATE_FILE = "slack_messages/cfn_deployment.json"
notifier = SlackNotifier(os.environ.get("DEPLOYMENT_WEBHOOK_URL"))
repo = AgentRepository()


def upsert_account(event: CfnStackEvent):
    try:
        repo.update(
            event.account,
            UpdateAgentDTO(
                region=event.region,
                status=event.stack_data.status,
                deployed_at=datetime_str_to_timestamp(event.time),
            ),
        )
    except NotFoundError:
        repo.create(
            Agent(
                id=event.account,
                region=event.region,
                status=event.stack_data.status,
                deployed_at=datetime_str_to_timestamp(event.time),
            )
        )
    except Exception as e:
        logger.error(f"Failed to upsert account {event.account}: {e}")


def push_notification(event: CfnStackEvent):
    match event.stack_data.status:
        case CfnStackStatus.CREATE_COMPLETE | CfnStackStatus.UPDATE_COMPLETE:
            emoji = ":rocket:"
            color = "#36A64F"
        case CfnStackStatus.CREATE_FAILED | CfnStackStatus.UPDATE_FAILED | CfnStackStatus.UPDATE_ROLLBACK_FAILED:
            emoji = ":x:"
            color = "#FF0000"
        case _:
            emoji = ":warning:"
            color = "#FFA500"

    message = render_message(
        TEMPLATE_FILE,
        context={
            "color": color,
            "emoji": emoji,
            "account": event.account,
            "region": event.region,
            "stack_name": event.stack_data.name,
            "stack_status": event.stack_data.status,
            "stack_status_reason": event.stack_data.status_reason,
            "time": event.time,
            "console_link": (
                f"https://console.aws.amazon.com/cloudformation/home?region={event.region}#/stacks/stackinfo?filtering"
                f"Status=active&filteringText={event.stack_data.name}&viewNested=true&stackId={event.stack_data.id}"
            ),
        },
    )
    notifier.notify(message)
    logger.info(f"Sent Event<{event.get_id}> notification")


@event_source(data_class=CfnStackEvent)
def handler(event: CfnStackEvent, context):
    """Handle the incoming event."""
    logger.debug(event.raw_event)

    if event.source == "aws.cloudformation":
        upsert_account(event)
        push_notification(event)

    else:
        logger.warning(f"Unsupported event source: {event.source}")
