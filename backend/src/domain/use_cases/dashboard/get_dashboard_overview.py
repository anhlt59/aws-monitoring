"""Get dashboard overview use case."""

from pydantic import Field

from src.adapters.db.repositories.event import EventRepository
from src.adapters.db.repositories.task import TaskRepository
from src.adapters.db.repositories.user import UserRepository
from src.common.models import BaseModel
from src.domain.use_cases.dashboard.get_events_stats import EventsStatsDTO, GetEventsStats
from src.domain.use_cases.dashboard.get_tasks_stats import GetTasksStats, TasksStatsDTO
from src.domain.use_cases.dashboard.get_users_stats import GetUsersStats, UsersStatsDTO


class DashboardOverviewDTO(BaseModel):
    """Dashboard overview response with all statistics."""

    events_stats: EventsStatsDTO = Field(..., description="Events statistics")
    tasks_stats: TasksStatsDTO = Field(..., description="Tasks statistics")
    users_stats: UsersStatsDTO = Field(..., description="Users statistics")


class GetDashboardOverview:
    """
    Use case for retrieving complete dashboard overview.

    Aggregates statistics from events, tasks, and users.
    """

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
        self.get_events_stats_uc = GetEventsStats(event_repository)
        self.get_tasks_stats_uc = GetTasksStats(task_repository)
        self.get_users_stats_uc = GetUsersStats(user_repository)

    def execute(
        self,
        start_date: int | None = None,
        end_date: int | None = None,
    ) -> DashboardOverviewDTO:
        """
        Get complete dashboard overview.

        Args:
            start_date: Filter data after this date (Unix timestamp)
            end_date: Filter data before this date (Unix timestamp)

        Returns:
            DashboardOverviewDTO with all statistics
        """
        # Get all statistics
        events_stats = self.get_events_stats_uc.execute(start_date, end_date)
        tasks_stats = self.get_tasks_stats_uc.execute(start_date, end_date)
        users_stats = self.get_users_stats_uc.execute()

        return DashboardOverviewDTO(
            events_stats=events_stats,
            tasks_stats=tasks_stats,
            users_stats=users_stats,
        )
