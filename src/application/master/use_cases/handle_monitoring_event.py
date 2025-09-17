from datetime import UTC, datetime

from src.common.logger import Logger
from src.domain.master.dtos.event_dtos import CreateEventDTO
from src.domain.master.entities.event import MonitoringEvent
from src.domain.master.ports.event_repository import EventRepository
from src.domain.master.ports.notifier import Notifier

logger = Logger(__name__)


class HandleMonitoringEventUseCase:
    """Use case for handling monitoring events"""

    def __init__(self, event_repository: EventRepository, notifier: Notifier):
        self.event_repository = event_repository
        self.notifier = notifier

    async def execute(self, event_dto: CreateEventDTO) -> MonitoringEvent:
        """Process a monitoring event"""
        try:
            # Create domain entity from DTO
            event = self._create_event_from_dto(event_dto)

            # Save event to repository
            await self.event_repository.save(event)
            logger.info(f"Event saved: {event.id} with severity: {event.severity}")

            # Handle critical events
            if event.is_critical():
                await self._handle_critical_event(event)

            # Handle events requiring immediate action
            if event.requires_immediate_action():
                await self._trigger_immediate_action(event)

            return event

        except Exception as e:
            logger.error(f"Failed to handle monitoring event: {e}")
            raise

    def _create_event_from_dto(self, dto: CreateEventDTO) -> MonitoringEvent:
        """Create domain entity from DTO"""
        # Use factory method if severity needs to be detected
        if dto.severity is None:
            return MonitoringEvent.from_aws_event(
                event_id=dto.id,
                account=dto.account,
                region=dto.region,
                source=dto.source,
                detail=dto.detail,
                detail_type=dto.detail_type,
                resources=dto.resources,
                published_at=dto.published_at or datetime.now(UTC),
            )

        # Direct creation if severity is provided
        return MonitoringEvent(
            id=dto.id,
            account=dto.account,
            region=dto.region,
            source=dto.source,
            detail=dto.detail,
            detail_type=dto.detail_type,
            severity=dto.severity,
            resources=dto.resources,
            published_at=dto.published_at or datetime.now(UTC),
        )

    async def _handle_critical_event(self, event: MonitoringEvent) -> None:
        """Handle critical severity events"""
        logger.warning(f"Critical event detected: {event.id} from {event.source}")

        # Send notification for critical event
        await self.notifier.notify_event(event)

        # Check for patterns requiring escalation
        recent_critical = await self.event_repository.find_critical_events(
            since=datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0), limit=10
        )

        if len(recent_critical) >= 5:
            await self.notifier.notify_critical_alert(
                title="Multiple Critical Events Detected",
                message=f"Detected {len(recent_critical)} critical events today",
                events=recent_critical,
            )

    async def _trigger_immediate_action(self, event: MonitoringEvent) -> None:
        """Trigger immediate action for critical events"""
        logger.critical(f"Immediate action required for event: {event.id}")

        # Additional logic for immediate actions
        # This could trigger automated remediation, page on-call, etc.
        await self.notifier.notify_critical_alert(
            title="IMMEDIATE ACTION REQUIRED",
            message=f"Critical event {event.id} requires immediate attention",
            events=[event],
        )
