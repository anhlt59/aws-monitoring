from src.adapters.db.models import AccountPersistence
from src.models import Account

from .base import BaseMapper


class AccountMapper(BaseMapper):
    @classmethod
    def to_persistence(cls, model: Account) -> AccountPersistence:
        return AccountPersistence(
            # Keys
            pk="ACCOUNT",
            sk=model.id,
            # Attributes
            region=model.region,
            status=model.status,
            deployed_at=model.deployed_at,
            created_at=model.created_at,
        )

    @classmethod
    def to_model(cls, persistence: AccountPersistence) -> Account:
        return Account(
            id=persistence.sk,
            region=persistence.region,
            status=persistence.status,
            deployed_at=persistence.deployed_at,
            created_at=persistence.created_at,
        )
