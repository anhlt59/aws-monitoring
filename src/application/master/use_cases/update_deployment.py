from datetime import UTC, datetime
from typing import Optional

from src.common.logger import Logger
from src.domain.master.dtos.agent_dtos import AgentDeploymentRequestDTO, AgentHealthDTO, UpdateAgentDTO
from src.domain.master.entities.agent import Agent
from src.domain.master.ports.agent_repository import AgentRepository
from src.domain.master.ports.notifier import Notifier

logger = Logger(__name__)


class UpdateDeploymentUseCase:
    """Use case for managing agent deployments"""

    def __init__(self, agent_repository: AgentRepository, notifier: Notifier):
        self.agent_repository = agent_repository
        self.notifier = notifier

    async def execute(self, request: AgentDeploymentRequestDTO) -> Agent:
        """Handle agent deployment update"""
        try:
            logger.info(f"Processing deployment for account {request.account}")

            # Find existing agent or create new one
            agent = await self._get_or_create_agent(request.account, request.region)

            # Update agent status to deployment in progress
            agent.mark_deployment_started()
            await self.agent_repository.save(agent)

            # Notify about deployment start
            await self.notifier.notify_agent_status(
                agent=agent, message=f"Deployment started for stack: {request.stack_name}"
            )

            logger.info(f"Agent deployment initiated for {request.account}")
            return agent

        except Exception as e:
            logger.error(f"Failed to update deployment for {request.account}: {e}")
            raise

    async def complete_deployment(self, account: str, success: bool = True) -> Agent:
        """Mark deployment as completed or failed"""
        try:
            agent = await self.agent_repository.find_by_account(account)
            if not agent:
                raise ValueError(f"Agent not found for account: {account}")

            if success:
                agent.mark_deployment_completed()
                message = "Deployment completed successfully"
                logger.info(f"Deployment completed for {account}")
            else:
                agent.mark_deployment_failed()
                message = "Deployment failed"
                logger.error(f"Deployment failed for {account}")

            await self.agent_repository.save(agent)

            # Notify about deployment result
            await self.notifier.notify_agent_status(agent=agent, message=message)

            return agent

        except Exception as e:
            logger.error(f"Failed to complete deployment for {account}: {e}")
            raise

    async def update_agent_status(self, account: str, update_dto: UpdateAgentDTO) -> Agent:
        """Update agent information"""
        try:
            agent = await self.agent_repository.find_by_account(account)
            if not agent:
                raise ValueError(f"Agent not found for account: {account}")

            # Update fields if provided
            if update_dto.region:
                agent.region = update_dto.region

            if update_dto.status:
                agent.update_status(update_dto.status)

            if update_dto.deployed_at:
                agent.deployed_at = update_dto.deployed_at

            await self.agent_repository.save(agent)

            logger.info(f"Agent {account} updated successfully")
            return agent

        except Exception as e:
            logger.error(f"Failed to update agent {account}: {e}")
            raise

    async def get_agent_health(self, account: str) -> AgentHealthDTO:
        """Get comprehensive agent health information"""
        try:
            agent = await self.agent_repository.find_by_account(account)
            if not agent:
                raise ValueError(f"Agent not found for account: {account}")

            # TODO: In a real implementation, you might want to check last heartbeat
            # from agent heartbeat events or other monitoring data
            last_heartbeat = self._calculate_last_heartbeat(agent)

            return AgentHealthDTO(
                account=agent.account,
                region=agent.region,
                status=agent.status,
                is_healthy=agent.is_healthy(),
                is_operational=agent.is_operational(),
                last_heartbeat=last_heartbeat,
                deployed_at=agent.deployed_at,
            )

        except Exception as e:
            logger.error(f"Failed to get agent health for {account}: {e}")
            raise

    async def delete_agent(self, account: str) -> bool:
        """Remove agent from monitoring"""
        try:
            agent = await self.agent_repository.find_by_account(account)
            if not agent:
                logger.warning(f"Agent {account} not found for deletion")
                return False

            # Mark for deletion
            agent.mark_deletion_started()
            await self.agent_repository.save(agent)

            # Notify about deletion
            await self.notifier.notify_agent_status(agent=agent, message="Agent removal initiated")

            # Actually delete after notification
            success = await self.agent_repository.delete(account)

            if success:
                logger.info(f"Agent {account} deleted successfully")
            else:
                logger.error(f"Failed to delete agent {account}")

            return success

        except Exception as e:
            logger.error(f"Failed to delete agent {account}: {e}")
            raise

    async def _get_or_create_agent(self, account: str, region: str) -> Agent:
        """Get existing agent or create new one"""
        agent = await self.agent_repository.find_by_account(account)

        if not agent:
            # Create new agent
            agent = Agent.create_new(account=account, region=region)
            logger.info(f"Created new agent for account {account}")

        return agent

    def _calculate_last_heartbeat(self, agent: Agent) -> Optional[datetime]:
        """Calculate last heartbeat time - placeholder for real implementation"""
        # In a real implementation, this would query event repository
        # for the most recent heartbeat event from this agent
        if agent.is_operational():
            # Assume operational agents have recent heartbeat
            return datetime.now(UTC)
        return None
