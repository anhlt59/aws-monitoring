from src.modules.master.models import Master
from src.modules.master.services.db.models import MasterPersistence


class MasterMapper:
    @classmethod
    def to_persistence(cls, model: Master) -> MasterPersistence:
        return MasterPersistence(
            # Keys
            pk="MASTER",
            sk=model.id,
            # Attributes
            region=model.region,
            status=model.status,
            deployed_at=model.deployed_at,
            created_at=model.created_at,
        )

    @classmethod
    def to_model(cls, persistence: MasterPersistence) -> Master:
        return Master(
            id=persistence.sk,
            region=persistence.region,
            status=persistence.status,
            deployed_at=persistence.deployed_at,
            created_at=persistence.created_at,
        )
