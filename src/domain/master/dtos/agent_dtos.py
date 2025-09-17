from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ..value_objects.agent_status import AgentStatus


class CreateAgentDTO(BaseModel):
    """DTO for creating a new agent"""

    account: str = Field(..., min_length=1, description="AWS Account ID")
    region: str = Field(..., min_length=1, description="AWS Region")


class UpdateAgentDTO(BaseModel):
    """DTO for updating agent information"""

    region: Optional[str] = Field(default=None, min_length=1, description="AWS Region")
    status: Optional[AgentStatus] = Field(default=None, description="Agent status")
    deployed_at: Optional[datetime] = Field(default=None, description="Deployment timestamp")


class AgentHealthDTO(BaseModel):
    """DTO for agent health status"""

    account: str = Field(..., description="AWS Account ID")
    region: str = Field(..., description="AWS Region")
    status: AgentStatus = Field(..., description="Current status")
    is_healthy: bool = Field(..., description="Health status")
    is_operational: bool = Field(..., description="Operational status")
    last_heartbeat: Optional[datetime] = Field(default=None, description="Last heartbeat timestamp")
    deployed_at: datetime = Field(..., description="Deployment timestamp")


class AgentDeploymentRequestDTO(BaseModel):
    """DTO for agent deployment request"""

    account: str = Field(..., min_length=1, description="AWS Account ID")
    region: str = Field(..., min_length=1, description="AWS Region")
    stack_name: str = Field(..., min_length=1, description="CloudFormation stack name")
    parameters: dict = Field(default_factory=dict, description="Deployment parameters")
