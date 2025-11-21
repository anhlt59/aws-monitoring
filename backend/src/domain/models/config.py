"""Configuration domain models and related enums."""

import re
from enum import Enum

from pydantic import Field, field_validator, model_validator

from src.common.models import BaseModel
from src.common.utils.datetime_utils import current_utc_timestamp


class AwsAccountStatus(str, Enum):
    """AWS Account deployment/monitoring status."""

    PENDING = "pending"  # Account registered, not deployed
    DEPLOYING = "deploying"  # Deployment in progress
    ACTIVE = "active"  # Deployed and monitoring
    FAILED = "failed"  # Deployment failed
    DISABLED = "disabled"  # Monitoring disabled


class AwsAccount(BaseModel):
    """
    AWS Account configuration for monitoring.

    Represents an AWS account that is being monitored.
    Note: Replaces previous "Agent" model - now includes deployment/monitoring status.
    """

    # Identity
    id: str  # Configuration UUID (not AWS account ID)
    account_id: str  # AWS Account ID (12 digits)
    account_name: str  # Friendly name

    # AWS Connection
    region: str  # Primary AWS region
    access_key_id: str | None = None  # AWS access key (encrypted)
    secret_access_key: str | None = None  # AWS secret key (encrypted)
    role_arn: str | None = None  # IAM role ARN (preferred)

    # Deployment/Monitoring Status (previously Agent fields)
    status: AwsAccountStatus = AwsAccountStatus.PENDING
    deployed_at: int | None = None  # When monitoring was deployed
    last_sync: int | None = None  # Last successful connection test
    is_active: bool = True  # Monitoring enabled/disabled

    # Timestamps
    created_at: int = Field(default_factory=current_utc_timestamp)
    updated_at: int = Field(default_factory=current_utc_timestamp)

    @property
    def persistence_id(self) -> str:
        """DynamoDB sort key for AWS account."""
        return self.id

    @field_validator("account_id")
    @classmethod
    def validate_account_id(cls, value: str) -> str:
        """Validate AWS Account ID format (12 digits)."""
        value = value.strip()
        if not value.isdigit() or len(value) != 12:
            raise ValueError("AWS Account ID must be 12 digits")
        return value

    @field_validator("account_name")
    @classmethod
    def validate_account_name(cls, value: str) -> str:
        """Validate account name is not empty."""
        value = value.strip()
        if not value or len(value) < 2:
            raise ValueError("Account name must be at least 2 characters")
        if len(value) > 100:
            raise ValueError("Account name cannot exceed 100 characters")
        return value

    @field_validator("region")
    @classmethod
    def validate_region(cls, value: str) -> str:
        """Validate AWS region format (e.g., us-east-1, eu-west-1)."""
        if not re.match(r"^[a-z]{2}-[a-z]+-\d{1}$", value):
            raise ValueError("Invalid AWS region format")
        return value

    @model_validator(mode="after")
    def validate_credentials(self):
        """
        Validate that credentials are provided.

        Must have either:
        - access_key_id + secret_access_key
        - OR role_arn
        """
        has_keys = self.access_key_id and self.secret_access_key
        has_role = self.role_arn

        if not (has_keys or has_role):
            raise ValueError("Must provide either access keys or role ARN")

        return self

    def uses_role_auth(self) -> bool:
        """Check if using IAM role authentication."""
        return self.role_arn is not None

    def uses_key_auth(self) -> bool:
        """Check if using access key authentication."""
        return self.access_key_id is not None

    def is_deployed(self) -> bool:
        """Check if account is deployed and actively monitoring."""
        return self.status == AwsAccountStatus.ACTIVE

    def is_pending_deployment(self) -> bool:
        """Check if account is awaiting deployment."""
        return self.status in (AwsAccountStatus.PENDING, AwsAccountStatus.DEPLOYING)

    def mark_deployed(self) -> None:
        """Mark account as successfully deployed."""
        self.status = AwsAccountStatus.ACTIVE
        self.deployed_at = current_utc_timestamp()
        self.updated_at = current_utc_timestamp()

    def mark_deployment_failed(self) -> None:
        """Mark account deployment as failed."""
        self.status = AwsAccountStatus.FAILED
        self.updated_at = current_utc_timestamp()

    def disable_monitoring(self) -> None:
        """Disable monitoring for this account."""
        self.status = AwsAccountStatus.DISABLED
        self.is_active = False
        self.updated_at = current_utc_timestamp()

    def enable_monitoring(self) -> None:
        """Re-enable monitoring for this account."""
        if self.deployed_at:
            self.status = AwsAccountStatus.ACTIVE
            self.is_active = True
            self.updated_at = current_utc_timestamp()

    def update_last_sync(self, success: bool) -> None:
        """Update last sync timestamp."""
        if success:
            self.last_sync = current_utc_timestamp()
        self.updated_at = current_utc_timestamp()

    def mask_credentials(self) -> dict:
        """Return account info with masked credentials for safe display."""
        data = self.model_dump()
        if self.access_key_id:
            data["access_key_id"] = f"{self.access_key_id[:4]}...{self.access_key_id[-4:]}"
        if self.secret_access_key:
            data["secret_access_key"] = "***REDACTED***"
        return data


class ServiceConfig(BaseModel):
    """Configuration for a specific AWS service."""

    service_name: str  # e.g., "cloudwatch", "guardduty"
    enabled: bool = True  # Service monitoring enabled

    # Polling configuration
    polling_interval: int = 300  # Seconds (default: 5 minutes)

    # Alert thresholds (service-specific)
    thresholds: dict = {}
    # Example for CloudWatch:
    # {
    #   "cpu_threshold": 80,
    #   "memory_threshold": 90,
    #   "error_rate_threshold": 5
    # }

    # Resource filtering
    resource_filters: dict = {}
    # {
    #   "resource_ids": ["i-1234567890", "db-instance-1"],
    #   "tags": {"Environment": "production", "Team": "platform"},
    #   "resource_types": ["AWS::EC2::Instance", "AWS::RDS::DBInstance"]
    # }

    # Severity rules
    severity_rules: list[dict] = []
    # [
    #   {
    #     "metric": "cpu_utilization",
    #     "operator": ">=",
    #     "value": 90,
    #     "severity": "critical"
    #   },
    #   {
    #     "metric": "cpu_utilization",
    #     "operator": ">=",
    #     "value": 70,
    #     "severity": "high"
    #   }
    # ]

    @field_validator("service_name")
    @classmethod
    def validate_service_name(cls, value: str) -> str:
        """Validate service name is not empty."""
        value = value.strip()
        if not value:
            raise ValueError("Service name cannot be empty")
        return value.lower()

    @field_validator("polling_interval")
    @classmethod
    def validate_polling_interval(cls, value: int) -> int:
        """Validate polling interval is reasonable (30s to 1 hour)."""
        if value < 30:
            raise ValueError("Polling interval cannot be less than 30 seconds")
        if value > 3600:
            raise ValueError("Polling interval cannot exceed 1 hour")
        return value


class MonitoringConfig(BaseModel):
    """
    Global monitoring configuration.

    Singleton configuration for the entire system.
    """

    # Service configurations
    services: list[ServiceConfig] = []

    # Global settings
    global_settings: dict = Field(
        default_factory=lambda: {
            "default_polling_interval": 300,  # 5 minutes
            "alert_email_enabled": True,
            "alert_email_recipients": [],
            "alert_slack_enabled": True,
            "alert_slack_webhook": "",
            "data_retention_days": 90,
            "event_batch_size": 100,
        }
    )

    # Timestamps
    updated_at: int = Field(default_factory=current_utc_timestamp)
    updated_by: str | None = None  # User ID who last updated

    @property
    def persistence_id(self) -> str:
        """DynamoDB sort key for monitoring config (singleton)."""
        return "MONITORING_CONFIG"

    @field_validator("services")
    @classmethod
    def validate_services(cls, value: list[ServiceConfig]) -> list[ServiceConfig]:
        """
        Validate services configuration.

        - No duplicate service names
        - At least one service enabled
        """
        if not value:
            return value

        service_names = [s.service_name for s in value]
        if len(service_names) != len(set(service_names)):
            raise ValueError("Duplicate service names not allowed")

        if not any(s.enabled for s in value):
            raise ValueError("At least one service must be enabled")

        return value

    def get_service_config(self, service_name: str) -> ServiceConfig | None:
        """Get configuration for a specific service."""
        for service in self.services:
            if service.service_name == service_name.lower():
                return service
        return None

    def is_service_enabled(self, service_name: str) -> bool:
        """Check if a service is enabled."""
        service = self.get_service_config(service_name)
        return service.enabled if service else False

    def update_service_config(self, service_name: str, config: ServiceConfig, updated_by: str) -> None:
        """Update or add service configuration."""
        for i, service in enumerate(self.services):
            if service.service_name == service_name.lower():
                self.services[i] = config
                self.updated_at = current_utc_timestamp()
                self.updated_by = updated_by
                return

        # Service not found, add it
        self.services.append(config)
        self.updated_at = current_utc_timestamp()
        self.updated_by = updated_by

    def get_enabled_services(self) -> list[ServiceConfig]:
        """Get list of enabled services."""
        return [s for s in self.services if s.enabled]

    def disable_service(self, service_name: str, updated_by: str) -> None:
        """Disable a specific service."""
        service = self.get_service_config(service_name)
        if service:
            service.enabled = False
            self.updated_at = current_utc_timestamp()
            self.updated_by = updated_by

    def enable_service(self, service_name: str, updated_by: str) -> None:
        """Enable a specific service."""
        service = self.get_service_config(service_name)
        if service:
            service.enabled = True
            self.updated_at = current_utc_timestamp()
            self.updated_by = updated_by
