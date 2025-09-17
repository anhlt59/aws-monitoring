from typing import List, Optional, Protocol

from ..entities.agent import Agent


class AgentRepository(Protocol):
    """Port for agent persistence operations"""

    async def save(self, agent: Agent) -> None:
        """Save an agent to the repository"""
        ...

    async def find_by_account(self, account: str) -> Optional[Agent]:
        """Find an agent by account ID"""
        ...

    async def find_all(self) -> List[Agent]:
        """Find all agents"""
        ...

    async def find_healthy_agents(self) -> List[Agent]:
        """Find all healthy agents"""
        ...

    async def find_failed_agents(self) -> List[Agent]:
        """Find all agents with failed status"""
        ...

    async def delete(self, account: str) -> bool:
        """Delete an agent by account ID, returns True if deleted"""
        ...

    async def exists(self, account: str) -> bool:
        """Check if agent exists for given account"""
        ...
