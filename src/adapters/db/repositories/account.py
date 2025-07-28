from src.adapters.db.mappers import AccountMapper
from src.adapters.db.models import AccountPersistence
from src.adapters.db.repositories.base import DynamoRepository, QueryResult
from src.models.account import Account, UpdateAccountDTO

AccountQueryResult = QueryResult[Account]


class AccountRepository(DynamoRepository):
    model_cls = AccountPersistence
    mapper = AccountMapper

    def get(self, id: str) -> Account:
        model = self._get(hash_key="ACCOUNT", range_key=id)
        return self.mapper.to_model(model)

    def list(self) -> AccountQueryResult:
        result = self._query(hash_key="ACCOUNT", limit=100)
        return AccountQueryResult(items=(self.mapper.to_model(project) for project in result))

    def create(self, entity: Account):
        model = AccountMapper.to_persistence(entity)
        self._create(model)

    def update(self, id: str, dto: UpdateAccountDTO):
        attributes = dto.model_dump(exclude_none=True)
        self._update(
            hash_key="ACCOUNT",
            range_key=id,
            attributes=attributes,
        )

    def delete(self, id: str):
        self._delete(hash_key="ACCOUNT", range_key=id)
