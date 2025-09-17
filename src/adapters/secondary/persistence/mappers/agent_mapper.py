from datetime import UTC, datetime
from typing import Any, Dict

from src.domain.master.entities.agent import Agent
from src.domain.master.value_objects.agent_status import AgentStatus


class AgentMapper:
    """Mapper for converting between Agent domain entity and DynamoDB items"""

    @staticmethod
    def to_dynamodb_item(agent: Agent) -> Dict[str, Any]:
        """Convert domain entity to DynamoDB item"""
        return {
            # DynamoDB keys
            "pk": "AGENT",
            "sk": f"AGENT#{agent.account}",
            # Agent data
            "region": agent.region,
            "status": agent.status.value,
            "deployed_at": int(agent.deployed_at.timestamp()),
            "created_at": int(agent.created_at.timestamp()),
            "updated_at": int(agent.updated_at.timestamp()) if agent.updated_at else None,
        }

    @staticmethod
    def to_domain_entity(item: Dict[str, Any]) -> Agent:
        """Convert DynamoDB item to domain entity"""
        # Extract account from sort key
        account = item["sk"].split("#", 1)[1]

        # Convert timestamps
        deployed_at = datetime.fromtimestamp(item["deployed_at"], tz=UTC)
        created_at = datetime.fromtimestamp(item["created_at"], tz=UTC)
        updated_at = None
        if item.get("updated_at"):
            updated_at = datetime.fromtimestamp(item["updated_at"], tz=UTC)

        # Convert status
        status = AgentStatus(item["status"])

        return Agent(
            account=account,
            region=item["region"],
            status=status,
            deployed_at=deployed_at,
            created_at=created_at,
            updated_at=updated_at,
        )
