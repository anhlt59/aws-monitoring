import time

import pytest

from src.common.configs import AWS_REGION, STAGE
from src.common.exceptions.http import NotFoundError
from src.models.account import Account, UpdateAccountDTO


def test_create_account(account_repo):
    account = Account(
        id="000000000000",
        name="TestAccount",
        stage=STAGE,
        region=AWS_REGION,
        deployed_at=int(time.time()),
    )
    account_repo.create(account)
    retrieved_account = account_repo.get(account.id)
    assert retrieved_account.id == account.id


def test_update_account(account_repo, dummy_account):
    update_dto = UpdateAccountDTO(name="UpdatedName", stage="updated-stage", region="ap-northeast-1")
    account_repo.update(dummy_account.id, update_dto)

    updated_account = account_repo.get(dummy_account.id)
    assert updated_account.name == update_dto.name
    assert updated_account.stage == update_dto.stage
    assert updated_account.region == update_dto.region


def test_delete_account(account_repo, dummy_account):
    account_repo.delete(dummy_account.id)
    with pytest.raises(NotFoundError):
        account_repo.get(dummy_account.id)


def test_list_accounts(account_repo, dummy_account):
    accounts = account_repo.list()
    assert len(accounts.items) > 0
    assert any(acc.id == dummy_account.id for acc in accounts.items)
