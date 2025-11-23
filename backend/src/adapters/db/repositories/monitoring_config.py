from src.adapters.db.mappers import MonitoringConfigMapper
from src.adapters.db.models import MonitoringConfigPersistence
from src.adapters.db.repositories.base import DynamoRepository
from src.domain.models import MonitoringConfig


class MonitoringConfigRepository(DynamoRepository):
    model_cls = MonitoringConfigPersistence
    mapper = MonitoringConfigMapper

    def get(self) -> MonitoringConfig:
        """Get monitoring configuration (singleton)."""
        model = self._get(hash_key="CONFIG", range_key="MONITORING")
        return self.mapper.to_entity(model)

    def create(self, entity: MonitoringConfig):
        """Create monitoring configuration."""
        model = self.mapper.to_persistence(entity)
        self._create(model)

    def update(self, entity: MonitoringConfig):
        """Update monitoring configuration."""
        model = self.mapper.to_persistence(entity)
        model.save()

    def delete(self):
        """Delete monitoring configuration."""
        self._delete(hash_key="CONFIG", range_key="MONITORING")
