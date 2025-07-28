from src.adapters.db.models import AccountPersistence
from src.models import Account

from .base import BaseMapper


class AccountMapper(BaseMapper):
    @classmethod
    def to_persistence(cls, model: Account) -> AccountPersistence:
        return AccountPersistence(
            # Keys
            pk="PROJECT",
            sk=model.id,
            # Attributes
            name=model.name,
            stage=model.stage,
            region=model.region,
            deployed_at=model.deployed_at,
            created_at=model.created_at,
        )

    @classmethod
    def to_model(cls, persistence: AccountPersistence) -> Account:
        return Account(
            id=persistence.sk,
            name=persistence.name,
            stage=persistence.stage,
            region=persistence.region,
            deployed_at=persistence.deployed_at,
            created_at=persistence.created_at,
        )
