import os

from aws_lambda_powertools.utilities.data_classes import event_source

from src.adapters.aws.data_classes import CfnStackEvent, CfnStackStatus
from src.adapters.db import AccountRepository
from src.adapters.notifiers import SlackNotifier
from src.common.logger import logger
from src.common.utils.datetime_utils import datetime_str_to_timestamp
from src.models.account import Account, UpdateAccountDTO

from .message import create_cfn_message

notifier = SlackNotifier(os.environ.get("DEPLOYMENT_WEBHOOK_URL"))
repo = AccountRepository()


def create_account(event: CfnStackEvent):
    model = Account(
        id=event.account,
        region=event.region,
        status=event.stack_status,
        deployed_at=datetime_str_to_timestamp(event.time),
    )
    repo.create(model)
    logger.info(f"Account<{model.id}> inserted")


def update_account(event: CfnStackEvent):
    dto = UpdateAccountDTO(
        region=event.region,
        status=event.stack_status,
        deployed_at=datetime_str_to_timestamp(event.time),
    )
    repo.update(event.account, dto)
    logger.info(f"Account<{event.account}> updated")


def delete_account(event: CfnStackEvent):
    repo.delete(event.account)
    logger.info(f"Account<{event.account}> deleted")


def push_notification(event: CfnStackEvent):
    message = create_cfn_message(event)
    notifier.notify(message)
    logger.info(f"Sent Event<{event.get_id}> notification")


# @logger.inject_lambda_context(log_event=True)
@event_source(data_class=CfnStackEvent)
def handler(event: CfnStackEvent, context):
    """Handle the incoming event."""
    logger.debug(event.raw_event)

    if event.source != "aws.cloudformation":
        logger.warning(f"Unsupported event source: {event.source}")
        return None

    match event.stack_status:
        case CfnStackStatus.CREATE_COMPLETE:
            logger.info(f"Stack {event.stack_name} created successfully.")
            create_account(event)
        case (
            CfnStackStatus.UPDATE_COMPLETE
            | CfnStackStatus.CREATE_FAILED
            | CfnStackStatus.UPDATE_FAILED
            | CfnStackStatus.DELETE_FAILED
        ):
            logger.info(f"Stack {event.stack_name} updated successfully.")
            update_account(event)
        case CfnStackStatus.DELETE_COMPLETE:
            logger.info(f"Stack {event.stack_name} deleted successfully.")
            delete_account(event)
        case _:
            logger.warning(f"Unhandled stack status: {event.stack_status}")

    push_notification(event)
    return None
