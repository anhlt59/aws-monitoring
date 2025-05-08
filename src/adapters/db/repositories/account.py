from src.adapters.db.mappers import AccountMapper
from src.adapters.db.models import AccountPersistence
from src.adapters.db.repositories.base import DynamoRepository, QueryResult
from src.common.exceptions.http import NotFoundError, UnprocessedError
from src.models import Account

AccountQueryResult = QueryResult[Account]


class AccountRepository(DynamoRepository):
    model_cls = AccountPersistence

    def get_by_id(self, project_id: str, account_id: str) -> Account:
        model = self._get(hash_key=project_id, range_key=account_id)
        return AccountMapper.to_entity(model)

    def list_by_project(
        self, project_id: str, limit: int = 50, direction: str = "asc", cursor: dict | None = None
    ) -> AccountQueryResult:
        result = self._query(
            hash_key=project_id,
            range_key_condition=AccountPersistence.sk.startswith("ACCOUNT#"),
            last_evaluated_key=cursor,
            scan_index_forward="asc" == direction,
            limit=limit,
        )
        return AccountQueryResult(
            items=[AccountMapper.to_entity(account) for account in result],
            limit=limit,
            cursor=result.last_evaluated_key,
        )

    def create(self, account: Account):
        model = AccountMapper.to_persistence(account)
        self._create(model)

    def update(self, project_id: str, account_id: str, attributes: dict):
        try:
            self._update(hash_key=project_id, range_key=account_id, attributes=attributes)
        except UnprocessedError:
            raise NotFoundError(f"Project<id={id}> not found")

    def delete(self, project_id: str, account_id: str):
        try:
            self._delete(hash_key=project_id, range_key=account_id)
        except UnprocessedError:
            raise NotFoundError(f"Account<project_id={project_id}, account_id={account_id}> not found")
