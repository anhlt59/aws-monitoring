from datetime import UTC, datetime, timedelta

import boto3
import pytest
from moto import mock_dynamodb

from src.adapters.secondary.persistence.dynamodb.event_repository import DynamoDBEventRepository
from src.domain.master.entities.event import MonitoringEvent
from src.domain.master.value_objects.severity import Severity


@mock_dynamodb
class TestDynamoDBEventRepositoryIntegration:
    """Integration tests for DynamoDB Event Repository"""

    @pytest.fixture
    def dynamodb_table(self):
        """Create a mock DynamoDB table for testing"""
        # Create mock DynamoDB resource
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        # Create table
        table = dynamodb.create_table(
            TableName="test-monitoring-table",
            KeySchema=[
                {"AttributeName": "pk", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "pk", "AttributeType": "S"},
                {"AttributeName": "sk", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        # Wait for table to be created
        table.wait_until_exists()
        return table

    @pytest.fixture
    def repository(self, dynamodb_table):
        """Create repository with test table"""
        return DynamoDBEventRepository(table_name="test-monitoring-table")

    @pytest.fixture
    def sample_event(self):
        """Sample monitoring event for testing"""
        return MonitoringEvent(
            id="test-event-123",
            account="123456789012",
            region="us-east-1",
            source="aws.cloudwatch",
            detail={"alarm": "test-alarm"},
            detail_type="CloudWatch Alarm",
            severity=Severity.HIGH,
            resources=["arn:aws:cloudwatch:us-east-1:123456789012:alarm:test"],
            published_at=datetime.now(UTC),
        )

    @pytest.mark.asyncio
    async def test_save_and_find_by_id(self, repository, sample_event, dynamodb_table):
        """Test saving an event and finding it by ID"""
        # Save event
        await repository.save(sample_event)

        # Verify item was saved to DynamoDB
        response = dynamodb_table.scan()
        assert response["Count"] == 1

        # Find by ID
        found_event = await repository.find_by_id(sample_event.id)

        # Verify found event
        assert found_event is not None
        assert found_event.id == sample_event.id
        assert found_event.account == sample_event.account
        assert found_event.severity == sample_event.severity

    @pytest.mark.asyncio
    async def test_find_by_time_range(self, repository, dynamodb_table):
        """Test finding events by time range"""
        now = datetime.now(UTC)

        # Create events with different timestamps
        events = [
            MonitoringEvent(
                id=f"event-{i}",
                account="123456789012",
                region="us-east-1",
                source="test.source",
                detail={},
                detail_type="Test Event",
                severity=Severity.MEDIUM,
                resources=[],
                published_at=now - timedelta(hours=i),
            )
            for i in range(5)
        ]

        # Save all events
        for event in events:
            await repository.save(event)

        # Find events in time range (last 3 hours)
        start_time = now - timedelta(hours=3)
        end_time = now + timedelta(hours=1)

        found_events = await repository.find_by_time_range(start_time, end_time)

        # Should find 4 events (0, 1, 2, 3 hours ago)
        assert len(found_events) == 4

        # Verify events are sorted by time (most recent first)
        for i in range(len(found_events) - 1):
            assert found_events[i].published_at >= found_events[i + 1].published_at

    @pytest.mark.asyncio
    async def test_find_by_account(self, repository, dynamodb_table):
        """Test finding events by account"""
        # Create events for different accounts
        account1_events = [
            MonitoringEvent(
                id=f"account1-event-{i}",
                account="111111111111",
                region="us-east-1",
                source="test.source",
                detail={},
                detail_type="Test Event",
                severity=Severity.LOW,
                resources=[],
                published_at=datetime.now(UTC),
            )
            for i in range(2)
        ]

        account2_events = [
            MonitoringEvent(
                id=f"account2-event-{i}",
                account="222222222222",
                region="us-east-1",
                source="test.source",
                detail={},
                detail_type="Test Event",
                severity=Severity.LOW,
                resources=[],
                published_at=datetime.now(UTC),
            )
            for i in range(3)
        ]

        # Save all events
        for event in account1_events + account2_events:
            await repository.save(event)

        # Find events for account1
        found_events = await repository.find_by_account("111111111111")

        # Should find 2 events for account1
        assert len(found_events) == 2
        for event in found_events:
            assert event.account == "111111111111"

    @pytest.mark.asyncio
    async def test_find_critical_events(self, repository, dynamodb_table):
        """Test finding critical events"""
        now = datetime.now(UTC)

        # Create events with different severities
        events = [
            MonitoringEvent(
                id="low-event",
                account="123456789012",
                region="us-east-1",
                source="test.source",
                detail={},
                detail_type="Test Event",
                severity=Severity.LOW,
                resources=[],
                published_at=now,
            ),
            MonitoringEvent(
                id="high-event",
                account="123456789012",
                region="us-east-1",
                source="test.source",
                detail={},
                detail_type="Test Event",
                severity=Severity.HIGH,
                resources=[],
                published_at=now,
            ),
            MonitoringEvent(
                id="critical-event",
                account="123456789012",
                region="us-east-1",
                source="test.source",
                detail={},
                detail_type="Test Event",
                severity=Severity.CRITICAL,
                resources=[],
                published_at=now,
            ),
        ]

        # Save all events
        for event in events:
            await repository.save(event)

        # Find critical events
        since = now - timedelta(hours=1)
        critical_events = await repository.find_critical_events(since)

        # Should find 2 critical events (HIGH and CRITICAL)
        assert len(critical_events) == 2
        for event in critical_events:
            assert event.severity.is_critical()

    @pytest.mark.asyncio
    async def test_count_by_time_range(self, repository, dynamodb_table):
        """Test counting events by time range"""
        now = datetime.now(UTC)

        # Create events
        events = [
            MonitoringEvent(
                id=f"count-event-{i}",
                account="123456789012",
                region="us-east-1",
                source="test.source",
                detail={},
                detail_type="Test Event",
                severity=Severity.LOW,
                resources=[],
                published_at=now - timedelta(hours=i),
            )
            for i in range(3)
        ]

        # Save all events
        for event in events:
            await repository.save(event)

        # Count events in last 2 hours
        start_time = now - timedelta(hours=2)
        end_time = now + timedelta(hours=1)

        count = await repository.count_by_time_range(start_time, end_time)

        # Should count 3 events (0, 1, 2 hours ago)
        assert count == 3

    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self, repository, dynamodb_table):
        """Test finding non-existent event by ID"""
        found_event = await repository.find_by_id("non-existent-event")
        assert found_event is None

    @pytest.mark.asyncio
    async def test_save_event_with_empty_resources(self, repository, dynamodb_table):
        """Test saving event with empty resources list"""
        event = MonitoringEvent(
            id="empty-resources-event",
            account="123456789012",
            region="us-east-1",
            source="test.source",
            detail={},
            detail_type="Test Event",
            severity=Severity.LOW,
            resources=[],  # Empty resources
            published_at=datetime.now(UTC),
        )

        # Should save without error
        await repository.save(event)

        # Verify it can be retrieved
        found_event = await repository.find_by_id(event.id)
        assert found_event is not None
        assert found_event.resources == []

    @pytest.mark.asyncio
    async def test_save_event_with_complex_detail(self, repository, dynamodb_table):
        """Test saving event with complex detail object"""
        complex_detail = {
            "nested": {"key": "value", "list": [1, 2, 3], "bool": True},
            "numbers": [1.5, 2.7, 3.14],
            "strings": ["a", "b", "c"],
        }

        event = MonitoringEvent(
            id="complex-detail-event",
            account="123456789012",
            region="us-east-1",
            source="test.source",
            detail=complex_detail,
            detail_type="Test Event",
            severity=Severity.LOW,
            resources=[],
            published_at=datetime.now(UTC),
        )

        # Should save without error
        await repository.save(event)

        # Verify detail is preserved
        found_event = await repository.find_by_id(event.id)
        assert found_event is not None
        assert found_event.detail == complex_detail
