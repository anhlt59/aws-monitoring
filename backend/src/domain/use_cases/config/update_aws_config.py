"""Update AWS configuration use case."""

from pydantic import Field

from src.adapters.db.repositories.aws_config import AWSConfigRepository
from src.common.models import BaseModel
from src.common.utils.datetime_utils import current_utc_timestamp
from src.domain.models.config import AWSConfig


class UpdateAwsConfigDTO(BaseModel):
    """Data transfer object for updating AWS config."""

    default_region: str | None = Field(None, description="Default AWS region")
    monitoring_account: str | None = Field(None, description="Monitoring AWS account ID")
    cross_account_role_name: str | None = Field(None, description="Cross-account IAM role name")


class UpdateAwsConfig:
    """
    Use case for updating AWS configuration.

    Updates singleton AWS config.
    Requires admin permissions.
    """

    def __init__(self, config_repository: AWSConfigRepository | None = None):
        """
        Initialize use case.

        Args:
            config_repository: AWS config repository instance
        """
        self.config_repository = config_repository or AWSConfigRepository()

    def execute(self, dto: UpdateAwsConfigDTO) -> AWSConfig:
        """
        Update AWS configuration.

        Args:
            dto: Update data

        Returns:
            Updated AWSConfig entity
        """
        # Fetch existing config (or create default)
        config = self.config_repository.get_singleton()
        if not config:
            # Create new config
            config = AWSConfig(
                default_region=dto.default_region or "us-east-1",
                monitoring_account=dto.monitoring_account or "",
                cross_account_role_name=dto.cross_account_role_name or "MonitoringRole",
            )
            self.config_repository.create(config)
            return config

        # Update fields if provided
        if dto.default_region is not None:
            config.default_region = dto.default_region

        if dto.monitoring_account is not None:
            config.monitoring_account = dto.monitoring_account

        if dto.cross_account_role_name is not None:
            config.cross_account_role_name = dto.cross_account_role_name

        # Update timestamp
        config.updated_at = current_utc_timestamp()

        # Save config
        self.config_repository.update(config)

        return config
