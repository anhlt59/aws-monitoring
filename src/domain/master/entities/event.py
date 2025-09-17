from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from ..value_objects.severity import Severity


class MonitoringEvent(BaseModel):
    """Core domain entity representing a monitoring event"""

    id: str = Field(..., min_length=1, description="Event ID")
    account: str = Field(..., min_length=1, description="AWS Account ID")
    region: str = Field(..., min_length=1, description="AWS Region")
    source: str = Field(..., min_length=1, description="Event source")
    detail: Dict[str, Any] = Field(default_factory=dict, description="Event detail payload")
    detail_type: str = Field(..., min_length=1, description="Event detail type")
    severity: Severity = Field(default=Severity.UNKNOWN, description="Event severity level")
    resources: List[str] = Field(default_factory=list, description="Associated resource ARNs")
    published_at: datetime = Field(..., description="Event publication timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

    @field_validator("id", "account", "source", "detail_type")
    @classmethod
    def validate_required_fields(cls, v: str) -> str:
        """Validate required string fields are not empty"""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    @model_validator(mode="after")
    def set_updated_at(self):
        """Auto-set updated_at if not provided"""
        if self.updated_at is None:
            self.updated_at = self.published_at
        return self

    def is_critical(self) -> bool:
        """Check if event severity is critical or high"""
        return self.severity.is_critical()

    def requires_immediate_action(self) -> bool:
        """Check if event requires immediate action"""
        return self.severity.requires_immediate_action()

    def is_aws_service_event(self) -> bool:
        """Check if event originates from AWS services"""
        return self.source.startswith("aws.")

    def get_primary_resource(self) -> Optional[str]:
        """Get the first resource ARN if available"""
        return self.resources[0] if self.resources else None

    def has_resources(self) -> bool:
        """Check if event has associated resources"""
        return bool(self.resources)

    def update_severity(self, new_severity: Severity) -> None:
        """Update event severity"""
        self.severity = new_severity
        self.updated_at = datetime.now(UTC)

    def add_resource(self, resource_arn: str) -> None:
        """Add a resource ARN to the event"""
        if resource_arn and resource_arn not in self.resources:
            self.resources.append(resource_arn)
            self.updated_at = datetime.now(UTC)

    @classmethod
    def from_aws_event(
        cls,
        event_id: str,
        account: str,
        region: str,
        source: str,
        detail: Dict[str, Any],
        detail_type: str,
        resources: List[str],
        published_at: datetime,
        severity: Optional[Severity] = None,
    ) -> "MonitoringEvent":
        """Factory method to create event from AWS EventBridge event"""
        # Auto-detect severity if not provided
        if severity is None:
            severity = cls._detect_severity(detail, detail_type)

        return cls(
            id=event_id,
            account=account,
            region=region,
            source=source,
            detail=detail,
            detail_type=detail_type,
            severity=severity,
            resources=resources,
            published_at=published_at,
        )

    @staticmethod
    def _detect_severity(detail: Dict[str, Any], detail_type: str) -> Severity:
        """Auto-detect severity based on event details"""
        # CloudWatch alarm severity detection
        if "state" in detail and "value" in detail.get("state", {}):
            alarm_state = detail["state"]["value"].upper()
            if alarm_state == "ALARM":
                return Severity.HIGH
            elif alarm_state == "OK":
                return Severity.LOW

        # ECS task failure detection
        if detail_type == "ECS Task State Change" and detail.get("lastStatus") == "STOPPED":
            exit_code = detail.get("containers", [{}])[0].get("exitCode", 0)
            if exit_code != 0:
                return Severity.MEDIUM

        # Default to unknown
        return Severity.UNKNOWN
