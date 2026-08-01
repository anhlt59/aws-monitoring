"""Get tasks statistics use case."""

from collections import defaultdict
from pydantic import Field

from src.adapters.db.repositories.task import TaskRepository
from src.common.models import BaseModel
from src.common.utils.datetime_utils import current_utc_timestamp


class TasksStatsDTO(BaseModel):
    """Tasks statistics response."""

    total: int = Field(..., description="Total number of tasks")
    by_status: dict[str, int] = Field(..., description="Count by status")
    by_priority: dict[str, int] = Field(..., description="Count by priority")
    overdue: int = Field(..., description="Number of overdue tasks")
    completion_rate: float = Field(..., description="Task completion rate (percentage)")


class GetTasksStats:
    """
    Use case for retrieving tasks statistics.

    Aggregates task data by status, priority, and calculates overdue tasks.
    """

    def __init__(self, task_repository: TaskRepository | None = None):
        """
        Initialize use case.

        Args:
            task_repository: Task repository instance
        """
        self.task_repository = task_repository or TaskRepository()

    def execute(self, start_date: int | None = None, end_date: int | None = None) -> TasksStatsDTO:
        """
        Get tasks statistics.

        Args:
            start_date: Filter tasks created after this date (Unix timestamp)
            end_date: Filter tasks created before this date (Unix timestamp)

        Returns:
            TasksStatsDTO with aggregated statistics
        """
        # Get all tasks
        tasks = self.task_repository.list_all()

        # Apply date filters if provided
        if start_date:
            tasks = [t for t in tasks if t.created_at >= start_date]
        if end_date:
            tasks = [t for t in tasks if t.created_at <= end_date]

        # Initialize counters
        by_status = defaultdict(int)
        by_priority = defaultdict(int)
        overdue_count = 0
        closed_count = 0

        # Current timestamp for overdue calculation
        now = current_utc_timestamp()

        # Aggregate statistics
        for task in tasks:
            by_status[task.status.value] += 1
            by_priority[task.priority.value] += 1

            # Count overdue tasks (not closed and past due date)
            if task.due_date and task.due_date < now and task.status.value != "closed":
                overdue_count += 1

            # Count closed tasks for completion rate
            if task.status.value == "closed":
                closed_count += 1

        # Calculate completion rate
        total_tasks = len(tasks)
        completion_rate = (closed_count / total_tasks * 100) if total_tasks > 0 else 0.0

        return TasksStatsDTO(
            total=total_tasks,
            by_status=dict(by_status),
            by_priority=dict(by_priority),
            overdue=overdue_count,
            completion_rate=round(completion_rate, 2),
        )
