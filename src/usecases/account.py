from src.adapters.db.repositories import AccountRepository
from src.common.utils.encoding import base64_to_json, json_to_base64
from src.models.account import Account, AccountCreateDTO, AccountUpdateDTO

account_repo = AccountRepository()


def get_account(project_id: str, account_id: str):
    return account_repo.get_by_id(project_id, account_id)


def list_accounts(project_id: str, limit=50, direction="asc", cursor: str | None = None):
    decode_cursor = base64_to_json(cursor) if cursor else None
    result = account_repo.list_by_project(project_id, limit, direction, decode_cursor)
    return {
        "items": result.items,
        "limit": limit,
        "next": json_to_base64(result.cursor) if result.cursor else None,
        "previous": cursor,
    }


def create_account(dto: AccountCreateDTO):
    account = Account.model_validate(dto, from_attributes=True)
    account_repo.create(account)
    return account


def update_account(project_id: str, account_id: str, dto: AccountUpdateDTO):
    account_repo.update(project_id, account_id, dto.model_dump())


def delete_account(project_id: str, account_id: str):
    account_repo.delete(project_id, account_id)
