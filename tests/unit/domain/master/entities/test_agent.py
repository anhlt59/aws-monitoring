from datetime import UTC, datetime

import pytest

from src.domain.master.entities.agent import Agent
from src.domain.master.value_objects.agent_status import AgentStatus


class TestAgent:
    """Test cases for Agent domain entity"""

    def test_create_agent(self):
        """Test creating an agent with all fields"""
        now = datetime.now(UTC)
        agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.CREATE_COMPLETE,
            deployed_at=now,
            created_at=now,
        )

        assert agent.account == "123456789012"
        assert agent.region == "us-east-1"
        assert agent.status == AgentStatus.CREATE_COMPLETE
        assert agent.deployed_at == now
        assert agent.created_at == now
        assert agent.updated_at == now  # Auto-set

    def test_agent_id_property(self):
        """Test agent ID property returns account"""
        now = datetime.now(UTC)
        agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.CREATE_COMPLETE,
            deployed_at=now,
            created_at=now,
        )

        assert agent.id == "123456789012"

    def test_validation_empty_account(self):
        """Test validation fails for empty account"""
        with pytest.raises(ValueError, match="Field cannot be empty"):
            Agent(
                account="",
                region="us-east-1",
                status=AgentStatus.CREATE_COMPLETE,
                deployed_at=datetime.now(UTC),
                created_at=datetime.now(UTC),
            )

    def test_validation_empty_region(self):
        """Test validation fails for empty region"""
        with pytest.raises(ValueError, match="Field cannot be empty"):
            Agent(
                account="123456789012",
                region="",
                status=AgentStatus.CREATE_COMPLETE,
                deployed_at=datetime.now(UTC),
                created_at=datetime.now(UTC),
            )

    def test_is_healthy_method(self):
        """Test is_healthy method for different statuses"""
        now = datetime.now(UTC)

        # CREATE_COMPLETE should be healthy
        healthy_agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.CREATE_COMPLETE,
            deployed_at=now,
            created_at=now,
        )
        assert healthy_agent.is_healthy() is True

        # UPDATE_COMPLETE should be healthy
        updated_agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.UPDATE_COMPLETE,
            deployed_at=now,
            created_at=now,
        )
        assert updated_agent.is_healthy() is True

        # CREATE_FAILED should not be healthy
        failed_agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.CREATE_FAILED,
            deployed_at=now,
            created_at=now,
        )
        assert failed_agent.is_healthy() is False

    def test_is_operational_method(self):
        """Test is_operational method"""
        now = datetime.now(UTC)

        # CREATE_COMPLETE should be operational
        operational_agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.CREATE_COMPLETE,
            deployed_at=now,
            created_at=now,
        )
        assert operational_agent.is_operational() is True

        # CREATE_IN_PROGRESS should not be operational (healthy but in progress)
        in_progress_agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.CREATE_IN_PROGRESS,
            deployed_at=now,
            created_at=now,
        )
        assert in_progress_agent.is_operational() is False

    def test_is_deployment_in_progress(self):
        """Test is_deployment_in_progress method"""
        now = datetime.now(UTC)

        # CREATE_IN_PROGRESS should be in progress
        in_progress_agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.CREATE_IN_PROGRESS,
            deployed_at=now,
            created_at=now,
        )
        assert in_progress_agent.is_deployment_in_progress() is True

        # CREATE_COMPLETE should not be in progress
        complete_agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.CREATE_COMPLETE,
            deployed_at=now,
            created_at=now,
        )
        assert complete_agent.is_deployment_in_progress() is False

    def test_has_deployment_failed(self):
        """Test has_deployment_failed method"""
        now = datetime.now(UTC)

        # CREATE_FAILED should have failed
        failed_agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.CREATE_FAILED,
            deployed_at=now,
            created_at=now,
        )
        assert failed_agent.has_deployment_failed() is True

        # CREATE_COMPLETE should not have failed
        success_agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.CREATE_COMPLETE,
            deployed_at=now,
            created_at=now,
        )
        assert success_agent.has_deployment_failed() is False

    def test_update_status(self):
        """Test update_status method"""
        now = datetime.now(UTC)
        agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.CREATE_IN_PROGRESS,
            deployed_at=now,
            created_at=now,
        )

        original_updated_at = agent.updated_at

        # Update status
        agent.update_status(AgentStatus.CREATE_COMPLETE)

        assert agent.status == AgentStatus.CREATE_COMPLETE
        assert agent.updated_at > original_updated_at

    def test_mark_deployment_started_new_agent(self):
        """Test mark_deployment_started for new agent"""
        now = datetime.now(UTC)
        agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.CREATE_COMPLETE,
            deployed_at=now,
            created_at=now,
        )

        # First deployment should go to CREATE_IN_PROGRESS
        agent.mark_deployment_started()
        assert agent.status == AgentStatus.UPDATE_IN_PROGRESS

    def test_mark_deployment_started_failed_agent(self):
        """Test mark_deployment_started for failed agent"""
        now = datetime.now(UTC)
        agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.CREATE_FAILED,
            deployed_at=now,
            created_at=now,
        )

        # Failed deployment should go to UPDATE_IN_PROGRESS
        agent.mark_deployment_started()
        assert agent.status == AgentStatus.UPDATE_IN_PROGRESS

    def test_mark_deployment_completed_create_flow(self):
        """Test mark_deployment_completed for create flow"""
        now = datetime.now(UTC)
        agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.CREATE_IN_PROGRESS,
            deployed_at=now,
            created_at=now,
        )

        original_deployed_at = agent.deployed_at

        # Complete CREATE flow
        agent.mark_deployment_completed()

        assert agent.status == AgentStatus.CREATE_COMPLETE
        assert agent.deployed_at > original_deployed_at

    def test_mark_deployment_completed_update_flow(self):
        """Test mark_deployment_completed for update flow"""
        now = datetime.now(UTC)
        agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.UPDATE_IN_PROGRESS,
            deployed_at=now,
            created_at=now,
        )

        # Complete UPDATE flow
        agent.mark_deployment_completed()
        assert agent.status == AgentStatus.UPDATE_COMPLETE

    def test_mark_deployment_failed_create_flow(self):
        """Test mark_deployment_failed for create flow"""
        now = datetime.now(UTC)
        agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.CREATE_IN_PROGRESS,
            deployed_at=now,
            created_at=now,
        )

        # Fail CREATE flow
        agent.mark_deployment_failed()
        assert agent.status == AgentStatus.CREATE_FAILED

    def test_mark_deployment_failed_update_flow(self):
        """Test mark_deployment_failed for update flow"""
        now = datetime.now(UTC)
        agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.UPDATE_IN_PROGRESS,
            deployed_at=now,
            created_at=now,
        )

        # Fail UPDATE flow
        agent.mark_deployment_failed()
        assert agent.status == AgentStatus.UPDATE_FAILED

    def test_mark_deletion_started(self):
        """Test mark_deletion_started method"""
        now = datetime.now(UTC)
        agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.CREATE_COMPLETE,
            deployed_at=now,
            created_at=now,
        )

        agent.mark_deletion_started()
        assert agent.status == AgentStatus.DELETE_IN_PROGRESS

    def test_mark_deleted(self):
        """Test mark_deleted method"""
        now = datetime.now(UTC)
        agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.DELETE_IN_PROGRESS,
            deployed_at=now,
            created_at=now,
        )

        agent.mark_deleted()
        assert agent.status == AgentStatus.DELETE_COMPLETE

    def test_mark_deletion_failed(self):
        """Test mark_deletion_failed method"""
        now = datetime.now(UTC)
        agent = Agent(
            account="123456789012",
            region="us-east-1",
            status=AgentStatus.DELETE_IN_PROGRESS,
            deployed_at=now,
            created_at=now,
        )

        agent.mark_deletion_failed()
        assert agent.status == AgentStatus.DELETE_FAILED

    def test_create_new_factory_method(self):
        """Test create_new factory method"""
        agent = Agent.create_new("123456789012", "us-east-1")

        assert agent.account == "123456789012"
        assert agent.region == "us-east-1"
        assert agent.status == AgentStatus.CREATE_IN_PROGRESS
        assert isinstance(agent.deployed_at, datetime)
        assert isinstance(agent.created_at, datetime)
        assert agent.deployed_at == agent.created_at
