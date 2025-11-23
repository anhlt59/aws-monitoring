from src.adapters.db.models import AwsConfigPersistence
from src.domain.models import AwsConfig


class AwsConfigMapper:
    @classmethod
    def to_persistence(cls, model: AwsConfig) -> AwsConfigPersistence:
        return AwsConfigPersistence(
            # Keys (Singleton)
            pk="CONFIG",
            sk="AWS",
            # Attributes
            id=model.id,
            account_id=model.account_id,
            account_name=model.account_name,
            region=model.region,
            role_arn=model.role_arn,
            status=model.status.value,
            deployed_at=model.deployed_at,
            last_sync=model.last_sync,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @classmethod
    def to_entity(cls, persistence: AwsConfigPersistence) -> AwsConfig:
        return AwsConfig(
            id=persistence.id,
            account_id=persistence.account_id,
            account_name=persistence.account_name,
            region=persistence.region,
            role_arn=persistence.role_arn,
            status=persistence.status,
            deployed_at=persistence.deployed_at,
            last_sync=persistence.last_sync,
            is_active=persistence.is_active,
            created_at=persistence.created_at,
            updated_at=persistence.updated_at,
        )
