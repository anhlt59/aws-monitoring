from src.adapters.db.mappers import AgentMapper
from src.adapters.db.models import AgentPersistence
from src.adapters.db.repositories.base import DynamoRepository
from src.common.exceptions import NotFoundError
from src.domain.models.agent import Agent, AgentQueryResult, UpdateAgentDTO


class AgentRepository(DynamoRepository):
    model_cls = AgentPersistence
    mapper = AgentMapper

    async def get(self, id: str) -> Agent:
        model = await self._get(hash_key="AGENT", range_key=id)
        return self.mapper.to_model(model)

    async def list(self) -> AgentQueryResult:
        result = await self._query(hash_key="AGENT", limit=100)
        return AgentQueryResult(items=[self.mapper.to_model(item) for item in result])

    async def create(self, entity: Agent):
        model = AgentMapper.to_persistence(entity)
        await self._create(model)

    async def update(self, id: str, dto: UpdateAgentDTO):
        if attributes := dto.model_dump(exclude_none=True):
            await self._update(
                hash_key="AGENT",
                range_key=id,
                attributes=attributes,
            )

    async def delete(self, id: str):
        await self._delete(hash_key="AGENT", range_key=id)

    async def exists(self, id: str) -> bool:
        try:
            await self._get(hash_key="AGENT", range_key=id, attributes_to_get=["pk", "sk"])
            return True
        except NotFoundError:
            return False
