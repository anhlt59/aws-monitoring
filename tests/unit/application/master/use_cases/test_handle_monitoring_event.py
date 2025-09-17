from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.master.use_cases.handle_monitoring_event import HandleMonitoringEventUseCase
from src.domain.master.dtos.event_dtos import CreateEventDTO
from src.domain.master.entities.event import MonitoringEvent
from src.domain.master.value_objects.severity import Severity


class TestHandleMonitoringEventUseCase:
    """Test cases for HandleMonitoringEventUseCase"""

    @pytest.fixture
    def mock_event_repository(self):
        """Mock event repository"""
        return AsyncMock()

    @pytest.fixture
    def mock_notifier(self):
        """Mock notifier"""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_event_repository, mock_notifier):
        """Create use case with mocked dependencies"""
        return HandleMonitoringEventUseCase(event_repository=mock_event_repository, notifier=mock_notifier)

    @pytest.fixture
    def sample_event_dto(self):
        """Sample event DTO for testing"""
        return CreateEventDTO(
            id="test-event-123",
            account="123456789012",
            region="us-east-1",
            source="aws.cloudwatch",
            detail={"alarm": "test"},
            detail_type="CloudWatch Alarm",
            severity=Severity.MEDIUM,
            resources=["arn:aws:cloudwatch:us-east-1:123456789012:alarm:test"],
        )

    @pytest.mark.asyncio
    async def test_execute_normal_event(self, use_case, mock_event_repository, mock_notifier, sample_event_dto):
        """Test executing use case with normal event"""
        # Execute use case
        result = await use_case.execute(sample_event_dto)

        # Verify result
        assert isinstance(result, MonitoringEvent)
        assert result.id == "test-event-123"
        assert result.account == "123456789012"
        assert result.severity == Severity.MEDIUM

        # Verify repository was called
        mock_event_repository.save.assert_called_once()
        saved_event = mock_event_repository.save.call_args[0][0]
        assert saved_event.id == "test-event-123"

        # Verify notifier was NOT called for non-critical event
        mock_notifier.notify_event.assert_not_called()
        mock_notifier.notify_critical_alert.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_critical_event(self, use_case, mock_event_repository, mock_notifier, sample_event_dto):
        """Test executing use case with critical event"""
        # Make event critical
        sample_event_dto.severity = Severity.CRITICAL

        # Mock repository to return empty list for recent critical events
        mock_event_repository.find_critical_events.return_value = []

        # Execute use case
        result = await use_case.execute(sample_event_dto)

        # Verify critical event handling
        assert result.severity == Severity.CRITICAL

        # Verify repository was called
        mock_event_repository.save.assert_called_once()

        # Verify notifier was called for critical event
        mock_notifier.notify_event.assert_called_once()

        # Verify critical alert was called for immediate action
        mock_notifier.notify_critical_alert.assert_called_once()
        args = mock_notifier.notify_critical_alert.call_args
        assert "IMMEDIATE ACTION REQUIRED" in args[1]["title"]

    @pytest.mark.asyncio
    async def test_execute_high_severity_event(self, use_case, mock_event_repository, mock_notifier, sample_event_dto):
        """Test executing use case with high severity event"""
        # Make event high severity
        sample_event_dto.severity = Severity.HIGH

        # Mock repository to return empty list for recent critical events
        mock_event_repository.find_critical_events.return_value = []

        # Execute use case
        result = await use_case.execute(sample_event_dto)

        # Verify high severity event handling
        assert result.severity == Severity.HIGH

        # Verify repository was called
        mock_event_repository.save.assert_called_once()

        # Verify notifier was called (high is critical)
        mock_notifier.notify_event.assert_called_once()

        # Verify immediate action was NOT called (only CRITICAL triggers immediate action)
        mock_notifier.notify_critical_alert.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_multiple_critical_events_alert(
        self, use_case, mock_event_repository, mock_notifier, sample_event_dto
    ):
        """Test alert when multiple critical events detected"""
        # Make event critical
        sample_event_dto.severity = Severity.CRITICAL

        # Mock repository to return multiple critical events
        mock_critical_events = [
            Mock(spec=MonitoringEvent, id=f"event-{i}", severity=Severity.CRITICAL) for i in range(5)
        ]
        mock_event_repository.find_critical_events.return_value = mock_critical_events

        # Execute use case
        await use_case.execute(sample_event_dto)

        # Verify multiple calls to notify_critical_alert
        assert mock_notifier.notify_critical_alert.call_count == 2  # One for immediate action, one for multiple events

        # Check the multiple events alert
        calls = mock_notifier.notify_critical_alert.call_args_list
        multiple_events_call = calls[0]  # First call should be multiple events
        assert "Multiple Critical Events Detected" in multiple_events_call[1]["title"]

    @pytest.mark.asyncio
    async def test_execute_auto_severity_detection(self, use_case, mock_event_repository, mock_notifier):
        """Test executing use case with auto severity detection"""
        # Create DTO without severity (should auto-detect)
        event_dto = CreateEventDTO(
            id="auto-detect-event",
            account="123456789012",
            region="us-east-1",
            source="aws.cloudwatch",
            detail={"state": {"value": "ALARM"}},  # Should auto-detect as HIGH
            detail_type="CloudWatch Alarm State Change",
            resources=[],
        )

        # Execute use case
        result = await use_case.execute(event_dto)

        # Verify severity was auto-detected
        assert result.severity == Severity.HIGH

    @pytest.mark.asyncio
    async def test_execute_with_published_at(self, use_case, mock_event_repository, mock_notifier):
        """Test executing use case with custom published_at"""
        custom_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)

        event_dto = CreateEventDTO(
            id="custom-time-event",
            account="123456789012",
            region="us-east-1",
            source="test.source",
            detail={},
            detail_type="Test Event",
            published_at=custom_time,
        )

        # Execute use case
        result = await use_case.execute(event_dto)

        # Verify custom time was used
        assert result.published_at == custom_time

    @pytest.mark.asyncio
    async def test_execute_repository_error(self, use_case, mock_event_repository, mock_notifier, sample_event_dto):
        """Test error handling when repository fails"""
        # Mock repository to raise error
        mock_event_repository.save.side_effect = Exception("Database error")

        # Execute use case and expect error
        with pytest.raises(Exception, match="Database error"):
            await use_case.execute(sample_event_dto)

        # Verify repository was called
        mock_event_repository.save.assert_called_once()

        # Verify notifier was not called due to error
        mock_notifier.notify_event.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_notifier_error_does_not_fail(
        self, use_case, mock_event_repository, mock_notifier, sample_event_dto
    ):
        """Test that notifier errors don't fail the main flow"""
        # Make event critical to trigger notification
        sample_event_dto.severity = Severity.CRITICAL

        # Mock notifier to raise error
        mock_notifier.notify_event.side_effect = Exception("Notification error")
        mock_event_repository.find_critical_events.return_value = []

        # Execute use case - should not raise error even if notification fails
        result = await use_case.execute(sample_event_dto)

        # Verify event was still saved despite notification error
        assert result.severity == Severity.CRITICAL
        mock_event_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_event_from_dto_minimal(self, use_case, mock_event_repository, mock_notifier):
        """Test creating event from DTO with minimal fields"""
        event_dto = CreateEventDTO(
            id="minimal-event",
            account="123456789012",
            region="us-east-1",
            source="test.source",
            detail={},
            detail_type="Test Event",
        )

        # Execute use case
        result = await use_case.execute(event_dto)

        # Verify defaults were set
        assert result.severity == Severity.UNKNOWN  # Auto-detected default
        assert result.resources == []
        assert isinstance(result.published_at, datetime)
        assert result.updated_at == result.published_at
