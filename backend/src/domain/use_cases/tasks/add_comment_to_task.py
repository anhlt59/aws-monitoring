"""Add comment to task use case."""

from uuid_utils import uuid7
from pydantic import Field

from src.adapters.db.repositories.task import TaskRepository
from src.adapters.db.repositories.user import UserRepository
from src.common.exceptions import NotFoundError
from src.common.models import BaseModel
from src.common.utils.datetime_utils import current_utc_timestamp
from src.domain.models.task import Task, TaskComment


class AddCommentDTO(BaseModel):
    """Data transfer object for adding comment."""

    task_id: str = Field(..., description="Task ID to add comment to")
    comment_text: str = Field(..., min_length=1, max_length=2000, description="Comment text")


class AddCommentToTask:
    """
    Use case for adding a comment to a task.

    Comments are stored as embedded array within the task entity.
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

    def execute(self, dto: AddCommentDTO, user_id: str) -> Task:
        """
        Add comment to task.

        Args:
            dto: Comment data
            user_id: User ID adding the comment

        Returns:
            Updated Task entity with new comment

        Raises:
            NotFoundError: If task or user not found
        """
        # Fetch task
        task = self.task_repository.get(dto.task_id)
        if not task:
            raise NotFoundError(f"Task not found: {dto.task_id}")

        # Fetch user to get name
        user = self.user_repository.get(user_id)
        if not user:
            raise NotFoundError(f"User not found: {user_id}")

        # Create comment object
        comment = TaskComment(
            id=str(uuid7()),
            user_id=user.id,
            user_name=user.full_name,
            comment=dto.comment_text.strip(),
            created_at=current_utc_timestamp(),
        )

        # Append comment to task's comments array
        task.comments.append(comment)

        # Update task timestamp
        task.updated_at = current_utc_timestamp()

        # Save task
        self.task_repository.update(task)

        return task
