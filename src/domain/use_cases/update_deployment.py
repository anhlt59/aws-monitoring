from src.common.logger import logger
from src.domain.models.agent import Agent, UpdateAgentDTO
from src.domain.ports import IAgentRepository, IEventNotifier


def update_deployment_use_case(
    account: str,
    region: str,
    status: str,
    deployed_at: int,
    event_data: dict,
    agent_repo: IAgentRepository,
    notifier: IEventNotifier,
):
    """Update deployment use-case.

    Updates agent deployment information and notifies subscribers.

    Args:
        account: AWS account ID
        region: AWS region where the deployment occurred
        status: CloudFormation stack status (e.g., CREATE_COMPLETE)
        deployed_at: Unix timestamp of deployment
        event_data: Original event data for notification
        agent_repo: Agent repository for persistence
        notifier: Event notifier for sending notifications

    Note:
        The entrypoint layer is responsible for extracting domain values
        from AWS-specific event structures (CfnStackEvent).
    """
    # 1. Insert/Update the agent information in the database.
    if agent_repo.exists(account):
        agent_repo.update(
            account,
            UpdateAgentDTO(
                region=region,
                status=status,
                deployed_at=deployed_at,
            ),
        )
    else:
        agent_repo.create(
            Agent(
                id=account,
                region=region,
                status=status,
                deployed_at=deployed_at,
            )
        )
    logger.info(f"Upserted Agent<{account}> successfully")

    # 2. Notify the event to the subscribers.
    notifier.notify(event_data)
    logger.info("Deployment event notification sent successfully")
