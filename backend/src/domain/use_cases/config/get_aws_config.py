"""Get AWS configuration use case."""

from src.adapters.db.repositories.aws_config import AWSConfigRepository
from src.domain.models.config import AWSConfig


class GetAwsConfig:
    """
    Use case for retrieving AWS configuration.

    Returns singleton AWS config, creates default if not exists.
    Requires admin permissions.
    """

    def __init__(self, config_repository: AWSConfigRepository | None = None):
        """
        Initialize use case.

        Args:
            config_repository: AWS config repository instance
        """
        self.config_repository = config_repository or AWSConfigRepository()

    def execute(self) -> AWSConfig:
        """
        Get AWS configuration.

        Returns:
            AWSConfig entity (singleton)
        """
        # Fetch singleton config
        config = self.config_repository.get_singleton()

        # Create default if not exists
        if not config:
            config = self._create_default_config()
            self.config_repository.create(config)

        return config

    def _create_default_config(self) -> AWSConfig:
        """Create default AWS configuration."""
        return AWSConfig(
            default_region="us-east-1",
            monitoring_account="",  # To be configured
            cross_account_role_name="MonitoringRole",
        )
