import json

from src.adapters.db.models import MonitoringConfigPersistence
from src.domain.models import MonitoringConfig, ServiceConfig


class MonitoringConfigMapper:
    @classmethod
    def to_persistence(cls, model: MonitoringConfig) -> MonitoringConfigPersistence:
        # Convert ServiceConfig list to JSON
        services_json = json.dumps([service.model_dump() for service in model.services])

        return MonitoringConfigPersistence(
            # Keys (Singleton)
            pk="CONFIG",
            sk="MONITORING",
            # Attributes
            services=services_json,
            global_settings=json.dumps(model.global_settings),
            updated_at=model.updated_at,
            updated_by=model.updated_by,
        )

    @classmethod
    def to_entity(cls, persistence: MonitoringConfigPersistence) -> MonitoringConfig:
        # Parse services JSON to ServiceConfig list
        services_data = json.loads(persistence.services)
        services = [ServiceConfig(**service_data) for service_data in services_data]

        return MonitoringConfig(
            services=services,
            global_settings=json.loads(persistence.global_settings),
            updated_at=persistence.updated_at,
            updated_by=persistence.updated_by,
        )
