from src.adapters.db.models.account import AccountPersistence
from src.models.account import Account

from .base import BaseMapper


class AccountMapper(BaseMapper):
    @classmethod
    def to_persistence(cls, model: Account) -> AccountPersistence:
        return AccountPersistence(
            pk=model.project_id,
            sk=model.id,
            name=model.name,
            active_regions=model.active_regions,
            assume_role_arn=model.assume_role_arn,
        )

    @classmethod
    def to_entity(cls, persistence: AccountPersistence) -> Account:
        return Account(
            id=persistence.sk,
            project_id=persistence.pk,
            name=persistence.name,
            active_regions=persistence.active_regions,
            assume_role_arn=persistence.assume_role_arn,
        )
