from src.modules.master.models import Agent
from src.modules.master.services.db.models import AgentPersistence


class AgentMapper:
    @classmethod
    def to_persistence(cls, model: Agent) -> AgentPersistence:
        return AgentPersistence(
            # Keys
            pk="AGENT",
            sk=model.id,
            # Attributes
            region=model.region,
            status=model.status,
            deployed_at=model.deployed_at,
            created_at=model.created_at,
        )

    @classmethod
    def to_model(cls, persistence: AgentPersistence) -> Agent:
        return Agent(
            id=persistence.sk,
            region=persistence.region,
            status=persistence.status,
            deployed_at=persistence.deployed_at,
            created_at=persistence.created_at,
        )
