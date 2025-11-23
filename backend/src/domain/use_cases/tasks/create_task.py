"""Create task use case."""

from uuid_utils import uuid7
from pydantic import Field

from src.adapters.db.repositories.task import TaskRepository
from src.adapters.db.repositories.user import UserRepository
from src.common.exceptions import NotFoundError
from src.common.models import BaseModel
from src.domain.models.task import AssignedUser, Task, TaskPriority, TaskStatus


class CreateTaskDTO(BaseModel):
    """Data transfer object for creating task."""

    title: str = Field(..., min_length=3, max_length=200, description="Task title")
    description: str = Field(..., min_length=10, max_length=5000, description="Task description")
    priority: TaskPriority = Field(..., description="Task priority")
    assigned_user_id: str = Field(..., description="User ID to assign task to")
    event_id: str | None = Field(None, description="Source event ID (optional)")
    event_details: dict | None = Field(None, description="Event details snapshot (optional)")
    due_date: int | None = Field(None, description="Due date timestamp (optional)")


class CreateTask:
    """
    Use case for creating a new task.

    Validates assigned user exists and creates task with initial status OPEN.
    """

    def __init__(
        self,
        task_repository: TaskRepository | None = None,
        user_repository: UserRepository | None = None,
    ):
        """
        Initialize use case.

        Args:
            task_repository: Task repository instance
            user_repository: User repository instance
        """
        self.task_repository = task_repository or TaskRepository()
        self.user_repository = user_repository or UserRepository()

    def execute(self, dto: CreateTaskDTO, created_by_user_id: str) -> Task:
        """
        Create a new task.

        Args:
            dto: Task creation data
            created_by_user_id: User ID of the user creating the task

        Returns:
            Created Task entity

        Raises:
            NotFoundError: If assigned user not found
        """
        # Validate assigned user exists
        assigned_user_entity = self.user_repository.get(dto.assigned_user_id)
        if not assigned_user_entity:
            raise NotFoundError(f"User not found: {dto.assigned_user_id}")

        # Create assigned user object
        assigned_user = AssignedUser(
            id=assigned_user_entity.id,
            name=assigned_user_entity.full_name,
        )

        # Create task entity
        task = Task(
            id=str(uuid7()),
            title=dto.title,
            description=dto.description,
            status=TaskStatus.OPEN,
            priority=dto.priority,
            assigned_user=assigned_user,
            event_id=dto.event_id,
            event_details=dto.event_details,
            due_date=dto.due_date,
            created_by=created_by_user_id,
            comments=[],  # Initialize empty comments array
        )

        # Save task
        self.task_repository.create(task)

        return task
