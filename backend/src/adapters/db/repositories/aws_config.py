from src.adapters.db.mappers import AwsConfigMapper
from src.adapters.db.models import AwsConfigPersistence
from src.adapters.db.repositories.base import DynamoRepository
from src.domain.models import AwsConfig


class AwsConfigRepository(DynamoRepository):
    model_cls = AwsConfigPersistence
    mapper = AwsConfigMapper

    def get(self) -> AwsConfig:
        """Get AWS configuration (singleton)."""
        model = self._get(hash_key="CONFIG", range_key="AWS")
        return self.mapper.to_entity(model)

    def create(self, entity: AwsConfig):
        """Create AWS configuration."""
        model = self.mapper.to_persistence(entity)
        self._create(model)

    def update(self, entity: AwsConfig):
        """Update AWS configuration."""
        model = self.mapper.to_persistence(entity)
        model.save()

    def delete(self):
        """Delete AWS configuration."""
        self._delete(hash_key="CONFIG", range_key="AWS")
