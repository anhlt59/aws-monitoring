"""Create task from event use case."""

from uuid_utils import uuid7

from pydantic import Field

from src.adapters.db.repositories.event import EventRepository
from src.adapters.db.repositories.task import TaskRepository
from src.adapters.db.repositories.user import UserRepository
from src.common.exceptions import NotFoundError
from src.common.models import BaseModel
from src.domain.models.task import AssignedUser, Task, TaskPriority
from src.domain.models.event import Event


class CreateTaskFromEventDTO(BaseModel):
    """Data transfer object for creating task from event."""

    event_id: str = Field(..., description="Source event ID")
    assigned_user_id: str = Field(..., description="User ID to assign task to")
    title: str | None = Field(None, description="Custom task title (auto-generated if not provided)")
    description: str | None = Field(None, description="Custom description (auto-generated if not provided)")
    priority: TaskPriority | None = Field(None, description="Task priority (mapped from event severity if not provided)")
    due_date: int | None = Field(None, description="Due date timestamp (optional)")


class CreateTaskFromEvent:
    """
    Use case for creating a task from a monitoring event.

    Maps event information to task fields:
    - Event severity -> Task priority
    - Event details -> Task description
    - Event metadata -> Task event_details
    """

    # Severity to priority mapping
    SEVERITY_TO_PRIORITY = {
        0: TaskPriority.LOW,      # info
        1: TaskPriority.LOW,      # low
        2: TaskPriority.MEDIUM,   # medium
        3: TaskPriority.HIGH,     # high
        4: TaskPriority.CRITICAL, # critical
        5: TaskPriority.CRITICAL, # critical
    }

    def __init__(
        self,
        event_repository: EventRepository | None = None,
        task_repository: TaskRepository | None = None,
        user_repository: UserRepository | None = None,
    ):
        """
        Initialize use case.

        Args:
            event_repository: Event repository instance
            task_repository: Task repository instance
            user_repository: User repository instance
        """
        self.event_repository = event_repository or EventRepository()
        self.task_repository = task_repository or TaskRepository()
        self.user_repository = user_repository or UserRepository()

    def execute(self, dto: CreateTaskFromEventDTO, created_by_user_id: str) -> Task:
        """
        Create a new task from an event.

        Args:
            dto: Task creation data
            created_by_user_id: User ID of the user creating the task

        Returns:
            Created Task entity

        Raises:
            NotFoundError: If event or assigned user not found
        """
        # Fetch event
        event = self.event_repository.get(dto.event_id)
        if not event:
            raise NotFoundError(f"Event not found: {dto.event_id}")

        # Fetch assigned user
        assigned_user_entity = self.user_repository.get(dto.assigned_user_id)
        if not assigned_user_entity:
            raise NotFoundError(f"User not found: {dto.assigned_user_id}")

        # Map priority from event severity if not provided
        priority = dto.priority or self._map_priority_from_severity(event.severity)

        # Generate title if not provided
        title = dto.title or self._generate_title(event)

        # Generate description if not provided
        description = dto.description or self._generate_description(event)

        # Create assigned user object
        assigned_user = AssignedUser(
            id=assigned_user_entity.id,
            name=assigned_user_entity.full_name,
        )

        # Create event details snapshot
        event_details = {
            "account": event.account,
            "region": event.region,
            "source": event.source,
            "severity": event.get_severity_label(),
            "detail_type": event.detail_type,
        }

        # Create task entity
        task = Task(
            id=str(uuid7()),
            title=title,
            description=description,
            priority=priority,
            assigned_user=assigned_user,
            event_id=event.id,
            event_details=event_details,
            due_date=dto.due_date,
            created_by=created_by_user_id,
            comments=[],  # Initialize empty comments array
        )

        # Save task
        self.task_repository.create(task)

        return task

    def _map_priority_from_severity(self, severity: int) -> TaskPriority:
        """
        Map event severity to task priority.

        Args:
            severity: Event severity level (0-5)

        Returns:
            TaskPriority enum value
        """
        return self.SEVERITY_TO_PRIORITY.get(severity, TaskPriority.MEDIUM)

    def _generate_title(self, event: Event) -> str:
        """
        Generate task title from event.

        Args:
            event: Event entity

        Returns:
            Generated task title
        """
        severity_label = event.get_severity_label().upper()
        source = event.source.replace("aws.", "").replace("monitoring.", "")
        return f"{severity_label}: {event.detail_type} in {source}"

    def _generate_description(self, event: Event) -> str:
        """
        Generate task description from event.

        Args:
            event: Event entity

        Returns:
            Generated task description
        """
        source = event.source
        severity_label = event.get_severity_label()

        description = f"A {severity_label} severity event was detected from {source}.\n\n"
        description += f"**Event Type:** {event.detail_type}\n"
        description += f"**Account:** {event.account}\n"
        description += f"**Region:** {event.region}\n\n"

        if event.resources:
            description += f"**Affected Resources:**\n"
            for resource in event.resources[:5]:  # Limit to 5 resources
                description += f"- {resource}\n"
            if len(event.resources) > 5:
                description += f"- ... and {len(event.resources) - 5} more\n"
            description += "\n"

        description += f"**Details:**\n"
        description += "Please investigate this event and take appropriate action.\n\n"
        description += f"_Auto-generated from event {event.id}_"

        return description
