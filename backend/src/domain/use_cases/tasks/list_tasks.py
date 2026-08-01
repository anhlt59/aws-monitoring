"""List tasks use case."""

from pydantic import Field

from src.adapters.db.repositories.task import TaskRepository
from src.common.models import BaseModel
from src.domain.models.task import Task, TaskPriority, TaskStatus


class ListTasksDTO(BaseModel):
    """Data transfer object for listing tasks."""

    status: TaskStatus | None = Field(None, description="Filter by status")
    priority: TaskPriority | None = Field(None, description="Filter by priority")
    assigned_user_id: str | None = Field(None, description="Filter by assigned user")
    start_date: int | None = Field(None, description="Filter tasks created after this date")
    end_date: int | None = Field(None, description="Filter tasks created before this date")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class PaginatedTasksDTO(BaseModel):
    """Paginated tasks response."""

    items: list[Task]
    total: int
    page: int
    page_size: int
    has_more: bool


class ListTasks:
    """
    Use case for listing tasks with filters and pagination.

    Supports filtering by status, priority, assigned user, and date range.
    """

    def __init__(self, task_repository: TaskRepository | None = None):
        """
        Initialize use case.

        Args:
            task_repository: Task repository instance
        """
        self.task_repository = task_repository or TaskRepository()

    def execute(self, dto: ListTasksDTO) -> PaginatedTasksDTO:
        """
        List tasks with filters.

        Args:
            dto: Filter and pagination parameters

        Returns:
            Paginated tasks response
        """
        # Use repository methods based on filters
        if dto.assigned_user_id:
            # Use GSI1 for assigned user queries
            tasks = self.task_repository.list_by_assigned_user(
                user_id=dto.assigned_user_id,
                status=dto.status,
            )
        elif dto.status:
            # Use GSI2 for status queries
            tasks = self.task_repository.list_by_status(
                status=dto.status,
                start_date=dto.start_date,
                end_date=dto.end_date,
            )
        else:
            # List all tasks
            tasks = self.task_repository.list_all()

        # Apply additional filters
        if dto.priority:
            tasks = [t for t in tasks if t.priority == dto.priority]

        if dto.start_date and not dto.status:
            tasks = [t for t in tasks if t.created_at >= dto.start_date]

        if dto.end_date and not dto.status:
            tasks = [t for t in tasks if t.created_at <= dto.end_date]

        # Calculate pagination
        total = len(tasks)
        start_idx = (dto.page - 1) * dto.page_size
        end_idx = start_idx + dto.page_size
        paginated_tasks = tasks[start_idx:end_idx]
        has_more = end_idx < total

        return PaginatedTasksDTO(
            items=paginated_tasks,
            total=total,
            page=dto.page,
            page_size=dto.page_size,
            has_more=has_more,
        )
