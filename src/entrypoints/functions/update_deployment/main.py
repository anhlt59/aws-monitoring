from src.adapters.aws.data_classes import CfnStackEvent, event_source
from src.adapters.db.repositories import AgentRepository
from src.adapters.notifiers import EventNotifier, SlackClient
from src.common.constants import DEPLOYMENT_WEBHOOK_URL
from src.common.logger import logger
from src.domain.use_cases.update_deployment import update_deployment_use_case

notifier = EventNotifier(client=SlackClient(DEPLOYMENT_WEBHOOK_URL))
agent_repo = AgentRepository()


# @logger.inject_lambda_context(log_event=True)
@event_source(data_class=CfnStackEvent)
def handler(event: CfnStackEvent, context):
    logger.debug(event.raw_event)

    try:
        update_deployment_use_case(event, agent_repo, notifier)
    except Exception as e:
        logger.error(f"Failed to process event: {e}")
