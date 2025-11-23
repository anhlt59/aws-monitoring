"""Update task status use case."""

from pydantic import Field

from src.adapters.db.repositories.task import TaskRepository
from src.common.exceptions import NotFoundError
from src.common.models import BaseModel
from src.common.utils.datetime_utils import current_utc_timestamp
from src.domain.models.task import Task, TaskStatus


class UpdateTaskStatusDTO(BaseModel):
    """Data transfer object for updating task status."""

    task_id: str = Field(..., description="Task ID to update")
    new_status: TaskStatus = Field(..., description="New task status")


class UpdateTaskStatus:
    """
    Use case for updating task status.

    Handles status transitions and manages closed_at timestamp.
    """

    def __init__(self, task_repository: TaskRepository | None = None):
        """
        Initialize use case.

        Args:
            task_repository: Task repository instance
        """
        self.task_repository = task_repository or TaskRepository()

    def execute(self, dto: UpdateTaskStatusDTO) -> Task:
        """
        Update task status.

        Args:
            dto: Status update data

        Returns:
            Updated Task entity

        Raises:
            NotFoundError: If task not found
        """
        # Fetch existing task
        task = self.task_repository.get(dto.task_id)
        if not task:
            raise NotFoundError(f"Task not found: {dto.task_id}")

        # Update status
        old_status = task.status
        task.status = dto.new_status

        # Manage closed_at timestamp
        if dto.new_status == TaskStatus.CLOSED and old_status != TaskStatus.CLOSED:
            # Task is being closed
            task.closed_at = current_utc_timestamp()
        elif dto.new_status != TaskStatus.CLOSED and old_status == TaskStatus.CLOSED:
            # Task is being reopened
            task.closed_at = None

        # Update timestamp
        task.updated_at = current_utc_timestamp()

        # Save task
        self.task_repository.update(task)

        return task
