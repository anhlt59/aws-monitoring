from datetime import UTC, datetime

import pytest

from src.domain.master.entities.event import MonitoringEvent
from src.domain.master.value_objects.severity import Severity


class TestMonitoringEvent:
    """Test cases for MonitoringEvent domain entity"""

    def test_create_monitoring_event(self):
        """Test creating a monitoring event with all fields"""
        now = datetime.now(UTC)
        event = MonitoringEvent(
            id="test-event-123",
            account="123456789012",
            region="us-east-1",
            source="aws.cloudwatch",
            detail={"alarm": "test"},
            detail_type="CloudWatch Alarm",
            severity=Severity.HIGH,
            resources=["arn:aws:cloudwatch:us-east-1:123456789012:alarm:test"],
            published_at=now,
        )

        assert event.id == "test-event-123"
        assert event.account == "123456789012"
        assert event.region == "us-east-1"
        assert event.source == "aws.cloudwatch"
        assert event.detail == {"alarm": "test"}
        assert event.detail_type == "CloudWatch Alarm"
        assert event.severity == Severity.HIGH
        assert len(event.resources) == 1
        assert event.published_at == now
        assert event.updated_at == now  # Auto-set

    def test_create_with_minimal_fields(self):
        """Test creating event with minimal required fields"""
        now = datetime.now(UTC)
        event = MonitoringEvent(
            id="minimal-event",
            account="123456789012",
            region="us-east-1",
            source="test.source",
            detail={},
            detail_type="Test Event",
            published_at=now,
        )

        assert event.severity == Severity.UNKNOWN  # Default
        assert event.resources == []  # Default
        assert event.updated_at == now

    def test_validation_empty_id(self):
        """Test validation fails for empty ID"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="String should have at least 1 character"):
            MonitoringEvent(
                id="",
                account="123456789012",
                region="us-east-1",
                source="test.source",
                detail={},
                detail_type="Test Event",
                published_at=datetime.now(UTC),
            )

    def test_validation_empty_account(self):
        """Test validation fails for empty account"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="String should have at least 1 character"):
            MonitoringEvent(
                id="test-event",
                account="",
                region="us-east-1",
                source="test.source",
                detail={},
                detail_type="Test Event",
                published_at=datetime.now(UTC),
            )

    def test_is_critical_method(self):
        """Test is_critical method for different severities"""
        now = datetime.now(UTC)

        # High severity should be critical
        high_event = MonitoringEvent(
            id="high-event",
            account="123456789012",
            region="us-east-1",
            source="test.source",
            detail={},
            detail_type="Test Event",
            severity=Severity.HIGH,
            published_at=now,
        )
        assert high_event.is_critical() is True

        # Critical severity should be critical
        critical_event = MonitoringEvent(
            id="critical-event",
            account="123456789012",
            region="us-east-1",
            source="test.source",
            detail={},
            detail_type="Test Event",
            severity=Severity.CRITICAL,
            published_at=now,
        )
        assert critical_event.is_critical() is True

        # Medium severity should not be critical
        medium_event = MonitoringEvent(
            id="medium-event",
            account="123456789012",
            region="us-east-1",
            source="test.source",
            detail={},
            detail_type="Test Event",
            severity=Severity.MEDIUM,
            published_at=now,
        )
        assert medium_event.is_critical() is False

    def test_requires_immediate_action_method(self):
        """Test requires_immediate_action method"""
        now = datetime.now(UTC)

        # Only CRITICAL should require immediate action
        critical_event = MonitoringEvent(
            id="critical-event",
            account="123456789012",
            region="us-east-1",
            source="test.source",
            detail={},
            detail_type="Test Event",
            severity=Severity.CRITICAL,
            published_at=now,
        )
        assert critical_event.requires_immediate_action() is True

        # HIGH should not require immediate action
        high_event = MonitoringEvent(
            id="high-event",
            account="123456789012",
            region="us-east-1",
            source="test.source",
            detail={},
            detail_type="Test Event",
            severity=Severity.HIGH,
            published_at=now,
        )
        assert high_event.requires_immediate_action() is False

    def test_is_aws_service_event(self):
        """Test is_aws_service_event method"""
        now = datetime.now(UTC)

        # AWS service event
        aws_event = MonitoringEvent(
            id="aws-event",
            account="123456789012",
            region="us-east-1",
            source="aws.cloudwatch",
            detail={},
            detail_type="Test Event",
            published_at=now,
        )
        assert aws_event.is_aws_service_event() is True

        # Non-AWS event
        custom_event = MonitoringEvent(
            id="custom-event",
            account="123456789012",
            region="us-east-1",
            source="custom.app",
            detail={},
            detail_type="Test Event",
            published_at=now,
        )
        assert custom_event.is_aws_service_event() is False

    def test_has_resources_method(self):
        """Test has_resources method"""
        now = datetime.now(UTC)

        # Event with resources
        event_with_resources = MonitoringEvent(
            id="event-with-resources",
            account="123456789012",
            region="us-east-1",
            source="test.source",
            detail={},
            detail_type="Test Event",
            resources=["arn:aws:resource"],
            published_at=now,
        )
        assert event_with_resources.has_resources() is True

        # Event without resources
        event_without_resources = MonitoringEvent(
            id="event-without-resources",
            account="123456789012",
            region="us-east-1",
            source="test.source",
            detail={},
            detail_type="Test Event",
            published_at=now,
        )
        assert event_without_resources.has_resources() is False

    def test_get_primary_resource(self):
        """Test get_primary_resource method"""
        now = datetime.now(UTC)

        # Event with multiple resources
        event = MonitoringEvent(
            id="multi-resource-event",
            account="123456789012",
            region="us-east-1",
            source="test.source",
            detail={},
            detail_type="Test Event",
            resources=["arn:aws:first", "arn:aws:second"],
            published_at=now,
        )
        assert event.get_primary_resource() == "arn:aws:first"

        # Event without resources
        empty_event = MonitoringEvent(
            id="empty-event",
            account="123456789012",
            region="us-east-1",
            source="test.source",
            detail={},
            detail_type="Test Event",
            published_at=now,
        )
        assert empty_event.get_primary_resource() is None

    def test_update_severity(self):
        """Test update_severity method"""
        now = datetime.now(UTC)
        event = MonitoringEvent(
            id="test-event",
            account="123456789012",
            region="us-east-1",
            source="test.source",
            detail={},
            detail_type="Test Event",
            severity=Severity.LOW,
            published_at=now,
        )

        original_updated_at = event.updated_at

        # Update severity
        event.update_severity(Severity.CRITICAL)

        assert event.severity == Severity.CRITICAL
        assert event.updated_at > original_updated_at

    def test_add_resource(self):
        """Test add_resource method"""
        now = datetime.now(UTC)
        event = MonitoringEvent(
            id="test-event",
            account="123456789012",
            region="us-east-1",
            source="test.source",
            detail={},
            detail_type="Test Event",
            published_at=now,
        )

        # Add new resource
        event.add_resource("arn:aws:new-resource")
        assert "arn:aws:new-resource" in event.resources

        # Adding duplicate should not duplicate
        event.add_resource("arn:aws:new-resource")
        assert event.resources.count("arn:aws:new-resource") == 1

    def test_from_aws_event_factory(self):
        """Test from_aws_event factory method"""
        now = datetime.now(UTC)

        event = MonitoringEvent.from_aws_event(
            event_id="factory-test",
            account="123456789012",
            region="us-east-1",
            source="aws.cloudwatch",
            detail={"state": {"value": "ALARM"}},
            detail_type="CloudWatch Alarm State Change",
            resources=["arn:aws:alarm"],
            published_at=now,
        )

        assert event.id == "factory-test"
        assert event.severity == Severity.HIGH  # Auto-detected from alarm state

    def test_severity_detection_cloudwatch_alarm(self):
        """Test severity auto-detection for CloudWatch alarms"""
        now = datetime.now(UTC)

        # ALARM state should be HIGH
        alarm_event = MonitoringEvent.from_aws_event(
            event_id="alarm-test",
            account="123456789012",
            region="us-east-1",
            source="aws.cloudwatch",
            detail={"state": {"value": "ALARM"}},
            detail_type="CloudWatch Alarm State Change",
            resources=[],
            published_at=now,
        )
        assert alarm_event.severity == Severity.HIGH

        # OK state should be LOW
        ok_event = MonitoringEvent.from_aws_event(
            event_id="ok-test",
            account="123456789012",
            region="us-east-1",
            source="aws.cloudwatch",
            detail={"state": {"value": "OK"}},
            detail_type="CloudWatch Alarm State Change",
            resources=[],
            published_at=now,
        )
        assert ok_event.severity == Severity.LOW

    def test_severity_detection_ecs_task_failure(self):
        """Test severity auto-detection for ECS task failures"""
        now = datetime.now(UTC)

        # Failed ECS task should be MEDIUM
        failed_task = MonitoringEvent.from_aws_event(
            event_id="ecs-fail-test",
            account="123456789012",
            region="us-east-1",
            source="aws.ecs",
            detail={"lastStatus": "STOPPED", "containers": [{"exitCode": 1}]},
            detail_type="ECS Task State Change",
            resources=[],
            published_at=now,
        )
        assert failed_task.severity == Severity.MEDIUM

        # Successful ECS task should be UNKNOWN (default)
        success_task = MonitoringEvent.from_aws_event(
            event_id="ecs-success-test",
            account="123456789012",
            region="us-east-1",
            source="aws.ecs",
            detail={"lastStatus": "STOPPED", "containers": [{"exitCode": 0}]},
            detail_type="ECS Task State Change",
            resources=[],
            published_at=now,
        )
        assert success_task.severity == Severity.UNKNOWN
