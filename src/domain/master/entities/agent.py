from datetime import UTC, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from ..value_objects.agent_status import AgentStatus


class Agent(BaseModel):
    """Core domain entity representing a monitoring agent"""

    account: str = Field(..., min_length=1, description="AWS Account ID")
    region: str = Field(..., min_length=1, description="AWS Region")
    status: AgentStatus = Field(..., description="Agent deployment status")
    deployed_at: datetime = Field(..., description="Deployment timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

    @field_validator("account", "region")
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
            self.updated_at = self.created_at
        return self

    @property
    def id(self) -> str:
        """Agent identifier based on account"""
        return self.account

    def is_healthy(self) -> bool:
        """Check if agent is in a healthy operational state"""
        return self.status.is_healthy()

    def is_operational(self) -> bool:
        """Check if agent is operational (healthy and not in progress)"""
        return self.status.is_healthy() and not self.status.is_in_progress()

    def is_deployment_in_progress(self) -> bool:
        """Check if agent deployment is in progress"""
        return self.status.is_in_progress()

    def has_deployment_failed(self) -> bool:
        """Check if agent deployment has failed"""
        return self.status.is_failed()

    def update_status(self, new_status: AgentStatus) -> None:
        """Update agent status with timestamp"""
        self.status = new_status
        self.updated_at = datetime.now(UTC)

    def mark_deployment_started(self) -> None:
        """Mark agent deployment as started"""
        if self.status in [AgentStatus.CREATE_COMPLETE, AgentStatus.CREATE_FAILED]:
            self.update_status(AgentStatus.UPDATE_IN_PROGRESS)
        else:
            self.update_status(AgentStatus.CREATE_IN_PROGRESS)

    def mark_deployment_completed(self) -> None:
        """Mark agent deployment as completed successfully"""
        self.deployed_at = datetime.now(UTC)
        if self.status == AgentStatus.CREATE_IN_PROGRESS:
            self.update_status(AgentStatus.CREATE_COMPLETE)
        else:
            self.update_status(AgentStatus.UPDATE_COMPLETE)

    def mark_deployment_failed(self) -> None:
        """Mark agent deployment as failed"""
        if self.status == AgentStatus.CREATE_IN_PROGRESS:
            self.update_status(AgentStatus.CREATE_FAILED)
        else:
            self.update_status(AgentStatus.UPDATE_FAILED)

    def mark_deletion_started(self) -> None:
        """Mark agent deletion as started"""
        self.update_status(AgentStatus.DELETE_IN_PROGRESS)

    def mark_deleted(self) -> None:
        """Mark agent as successfully deleted"""
        self.update_status(AgentStatus.DELETE_COMPLETE)

    def mark_deletion_failed(self) -> None:
        """Mark agent deletion as failed"""
        self.update_status(AgentStatus.DELETE_FAILED)

    @classmethod
    def create_new(cls, account: str, region: str) -> "Agent":
        """Factory method to create a new agent"""
        now = datetime.now(UTC)
        return cls(
            account=account, region=region, status=AgentStatus.CREATE_IN_PROGRESS, deployed_at=now, created_at=now
        )
