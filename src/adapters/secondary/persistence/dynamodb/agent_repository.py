from typing import List, Optional

from src.adapters.secondary.persistence.dynamodb.base_repository import BaseDynamoDBRepository
from src.adapters.secondary.persistence.mappers.agent_mapper import AgentMapper
from src.common.logger import logger
from src.domain.master.entities.agent import Agent
from src.domain.master.ports.agent_repository import AgentRepository




class DynamoDBAgentRepository(BaseDynamoDBRepository, AgentRepository):
    """DynamoDB implementation of AgentRepository port"""

    def __init__(self, table_name: Optional[str] = None):
        super().__init__(table_name)
        self.mapper = AgentMapper()

    async def save(self, agent: Agent) -> None:
        """Save an agent to DynamoDB"""
        try:
            item = self.mapper.to_dynamodb_item(agent)
            await self._put_item(item)
            logger.debug(f"Agent saved: {agent.account}")
        except Exception as e:
            logger.error(f"Failed to save agent {agent.account}: {e}")
            raise

    async def find_by_account(self, account: str) -> Optional[Agent]:
        """Find an agent by account ID"""
        try:
            key = {"pk": "AGENT", "sk": f"AGENT#{account}"}
            item = await self._get_item(key)

            if item:
                return self.mapper.to_domain_entity(item)
            return None

        except Exception as e:
            logger.error(f"Failed to find agent {account}: {e}")
            raise

    async def find_all(self) -> List[Agent]:
        """Find all agents"""
        try:
            items = await self._query(
                key_condition_expression="pk = :pk",
                expression_attribute_values={":pk": "AGENT"},
            )

            agents = [self.mapper.to_domain_entity(item) for item in items]
            logger.debug(f"Found {len(agents)} agents")
            return agents

        except Exception as e:
            logger.error(f"Failed to find all agents: {e}")
            raise

    async def find_healthy_agents(self) -> List[Agent]:
        """Find all healthy agents"""
        try:
            all_agents = await self.find_all()
            healthy_agents = [agent for agent in all_agents if agent.is_healthy()]

            logger.debug(f"Found {len(healthy_agents)} healthy agents")
            return healthy_agents

        except Exception as e:
            logger.error(f"Failed to find healthy agents: {e}")
            raise

    async def find_failed_agents(self) -> List[Agent]:
        """Find all agents with failed status"""
        try:
            all_agents = await self.find_all()
            failed_agents = [agent for agent in all_agents if agent.has_deployment_failed()]

            logger.debug(f"Found {len(failed_agents)} failed agents")
            return failed_agents

        except Exception as e:
            logger.error(f"Failed to find failed agents: {e}")
            raise

    async def delete(self, account: str) -> bool:
        """Delete an agent by account ID"""
        try:
            key = {"pk": "AGENT", "sk": f"AGENT#{account}"}
            success = await self._delete_item(key)

            if success:
                logger.info(f"Agent {account} deleted successfully")
            else:
                logger.warning(f"Failed to delete agent {account}")

            return success

        except Exception as e:
            logger.error(f"Failed to delete agent {account}: {e}")
            return False

    async def exists(self, account: str) -> bool:
        """Check if agent exists for given account"""
        try:
            agent = await self.find_by_account(account)
            return agent is not None

        except Exception as e:
            logger.error(f"Failed to check if agent {account} exists: {e}")
            return False
