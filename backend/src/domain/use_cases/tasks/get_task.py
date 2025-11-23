"""Get task use case."""

from src.adapters.db.repositories.task import TaskRepository
from src.common.exceptions import NotFoundError
from src.domain.models.task import Task


class GetTask:
    """
    Use case for retrieving a task by ID.

    Returns task with all embedded comments.
    """

    def __init__(self, task_repository: TaskRepository | None = None):
        """
        Initialize use case.

        Args:
            task_repository: Task repository instance
        """
        self.task_repository = task_repository or TaskRepository()

    def execute(self, task_id: str) -> Task:
        """
        Get task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task entity with all comments

        Raises:
            NotFoundError: If task not found
        """
        task = self.task_repository.get(task_id)

        if not task:
            raise NotFoundError(f"Task not found: {task_id}")

        return task
