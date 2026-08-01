"""Update monitoring configuration use case."""

from pydantic import Field

from src.adapters.db.repositories.monitoring_config import MonitoringConfigRepository
from src.common.models import BaseModel
from src.common.utils.datetime_utils import current_utc_timestamp
from src.domain.models.config import MonitoringConfig


class UpdateMonitoringConfigDTO(BaseModel):
    """Data transfer object for updating monitoring config."""

    query_duration: int | None = Field(None, ge=60, le=3600, description="Query duration in seconds (60-3600)")
    chunk_size: int | None = Field(None, ge=1, le=50, description="Number of log groups per query (1-50)")
    query_string: str | None = Field(None, description="CloudWatch Logs Insights query string")


class UpdateMonitoringConfig:
    """
    Use case for updating monitoring configuration.

    Updates singleton monitoring config.
    Requires admin permissions.
    """

    def __init__(self, config_repository: MonitoringConfigRepository | None = None):
        """
        Initialize use case.

        Args:
            config_repository: Monitoring config repository instance
        """
        self.config_repository = config_repository or MonitoringConfigRepository()

    def execute(self, dto: UpdateMonitoringConfigDTO) -> MonitoringConfig:
        """
        Update monitoring configuration.

        Args:
            dto: Update data

        Returns:
            Updated MonitoringConfig entity
        """
        # Fetch existing config (or create default)
        config = self.config_repository.get_singleton()
        if not config:
            # Create new config
            config = MonitoringConfig(
                query_duration=dto.query_duration or 300,
                chunk_size=dto.chunk_size or 10,
                query_string=dto.query_string or 'fields @timestamp, @message | filter @message like /ERROR/',
            )
            self.config_repository.create(config)
            return config

        # Update fields if provided
        if dto.query_duration is not None:
            config.query_duration = dto.query_duration

        if dto.chunk_size is not None:
            config.chunk_size = dto.chunk_size

        if dto.query_string is not None:
            config.query_string = dto.query_string

        # Update timestamp
        config.updated_at = current_utc_timestamp()

        # Save config
        self.config_repository.update(config)

        return config
