import time

import pytest

from src.adapters.aws.cloudformation import CfnStackStatus
from src.common.configs import AWS_REGION
from src.common.exceptions.http import NotFoundError
from src.models.account import Account, UpdateAccountDTO


def test_create_account(account_repo):
    account = Account(
        id="000000000000",
        region=AWS_REGION,
        status=CfnStackStatus.CREATE_COMPLETE,
        deployed_at=int(time.time()),
    )
    account_repo.create(account)
    retrieved_account = account_repo.get(account.id)
    assert retrieved_account.id == account.id


def test_update_account(account_repo, dummy_account):
    account_repo.get(dummy_account.id)

    update_dto = UpdateAccountDTO(status=CfnStackStatus.UPDATE_COMPLETE, region="ap-northeast-1")
    account_repo.update(dummy_account.id, update_dto)

    updated_account = account_repo.get(dummy_account.id)
    assert updated_account.status == update_dto.status
    assert updated_account.region == update_dto.region


def test_delete_account(account_repo, dummy_account):
    account_repo.delete(dummy_account.id)
    with pytest.raises(NotFoundError):
        account_repo.get(dummy_account.id)


def test_list_accounts(account_repo, dummy_account):
    accounts = account_repo.list()
    assert len(accounts.items) > 0
    assert any(acc.id == dummy_account.id for acc in accounts.items)
