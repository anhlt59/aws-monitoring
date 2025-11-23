"""Dashboard statistics use cases."""

from src.domain.use_cases.dashboard.get_dashboard_overview import GetDashboardOverview, DashboardOverviewDTO
from src.domain.use_cases.dashboard.get_events_stats import GetEventsStats, EventsStatsDTO
from src.domain.use_cases.dashboard.get_tasks_stats import GetTasksStats, TasksStatsDTO
from src.domain.use_cases.dashboard.get_users_stats import GetUsersStats, UsersStatsDTO

__all__ = [
    "GetDashboardOverview",
    "DashboardOverviewDTO",
    "GetEventsStats",
    "EventsStatsDTO",
    "GetTasksStats",
    "TasksStatsDTO",
    "GetUsersStats",
    "UsersStatsDTO",
]
