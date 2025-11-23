"""Get monitoring configuration use case."""

from src.adapters.db.repositories.monitoring_config import MonitoringConfigRepository
from src.domain.models.config import MonitoringConfig


class GetMonitoringConfig:
    """
    Use case for retrieving monitoring configuration.

    Returns singleton monitoring config, creates default if not exists.
    Requires admin permissions.
    """

    def __init__(self, config_repository: MonitoringConfigRepository | None = None):
        """
        Initialize use case.

        Args:
            config_repository: Monitoring config repository instance
        """
        self.config_repository = config_repository or MonitoringConfigRepository()

    def execute(self) -> MonitoringConfig:
        """
        Get monitoring configuration.

        Returns:
            MonitoringConfig entity (singleton)
        """
        # Fetch singleton config
        config = self.config_repository.get_singleton()

        # Create default if not exists
        if not config:
            config = self._create_default_config()
            self.config_repository.create(config)

        return config

    def _create_default_config(self) -> MonitoringConfig:
        """Create default monitoring configuration."""
        return MonitoringConfig(
            query_duration=300,  # 5 minutes
            chunk_size=10,  # 10 log groups per query
            query_string='fields @timestamp, @message | filter @message like /ERROR/',
        )
