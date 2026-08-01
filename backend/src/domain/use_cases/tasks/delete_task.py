"""Delete task use case."""

from src.adapters.db.repositories.task import TaskRepository
from src.common.exceptions import NotFoundError


class DeleteTask:
    """
    Use case for deleting a task.

    Requires admin permissions.
    """

    def __init__(self, task_repository: TaskRepository | None = None):
        """
        Initialize use case.

        Args:
            task_repository: Task repository instance
        """
        self.task_repository = task_repository or TaskRepository()

    def execute(self, task_id: str) -> bool:
        """
        Delete task by ID.

        Args:
            task_id: Task ID to delete

        Returns:
            True if deleted successfully

        Raises:
            NotFoundError: If task not found
        """
        # Verify task exists
        task = self.task_repository.get(task_id)
        if not task:
            raise NotFoundError(f"Task not found: {task_id}")

        # Delete task
        self.task_repository.delete(task_id)

        return True
