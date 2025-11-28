"""Update task use case."""

from pydantic import Field

from src.adapters.db.repositories.task import TaskRepository
from src.adapters.db.repositories.user import UserRepository
from src.common.exceptions import NotFoundError, UnauthorizedError
from src.common.models import BaseModel
from src.domain.models.task import AssignedUser, Task, TaskPriority


class UpdateTaskDTO(BaseModel):
    """Data transfer object for updating task."""

    task_id: str = Field(..., description="Task ID to update")
    title: str | None = Field(None, min_length=3, max_length=200, description="Task title")
    description: str | None = Field(None, min_length=10, max_length=5000, description="Task description")
    priority: TaskPriority | None = Field(None, description="Task priority")
    assigned_user_id: str | None = Field(None, description="User ID to assign task to")
    due_date: int | None = Field(None, description="Due date timestamp")


class UpdateTask:
    """
    Use case for updating task fields.

    Validates user permissions (owner or admin) before updating.
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

    def execute(self, dto: UpdateTaskDTO, requesting_user_id: str, is_admin: bool = False) -> Task:
        """
        Update task fields.

        Args:
            dto: Update data
            requesting_user_id: User ID making the request
            is_admin: Whether requesting user is admin

        Returns:
            Updated Task entity

        Raises:
            NotFoundError: If task or user not found
            UnauthorizedError: If user lacks permission to update
        """
        # Fetch existing task
        task = self.task_repository.get(dto.task_id)
        if not task:
            raise NotFoundError(f"Task not found: {dto.task_id}")

        # Check permissions (owner or admin)
        if not is_admin and task.created_by != requesting_user_id:
            raise UnauthorizedError("You can only update tasks you created")

        # Update fields if provided
        if dto.title is not None:
            task.title = dto.title

        if dto.description is not None:
            task.description = dto.description

        if dto.priority is not None:
            task.priority = dto.priority

        if dto.assigned_user_id is not None:
            # Validate new assigned user exists
            assigned_user_entity = self.user_repository.get(dto.assigned_user_id)
            if not assigned_user_entity:
                raise NotFoundError(f"User not found: {dto.assigned_user_id}")

            # Update assigned user
            task.assigned_user = AssignedUser(
                id=assigned_user_entity.id,
                name=assigned_user_entity.full_name,
            )

        if dto.due_date is not None:
            task.due_date = dto.due_date

        # Update timestamp
        from src.common.utils.datetime_utils import current_utc_timestamp

        task.updated_at = current_utc_timestamp()

        # Save task
        self.task_repository.update(task)

        return task
