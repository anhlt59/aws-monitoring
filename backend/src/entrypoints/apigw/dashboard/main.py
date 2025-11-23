"""Dashboard API Gateway handlers."""

from http import HTTPStatus
from typing import Annotated

from aws_lambda_powertools.event_handler.openapi.params import Query
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.domain.use_cases.dashboard import (
    GetDashboardOverview,
    GetEventsStats,
    GetTasksStats,
    GetUsersStats,
)
from src.entrypoints.apigw.base import create_app
from src.entrypoints.apigw.configs import CORS_ALLOW_ORIGIN, CORS_MAX_AGE
from src.entrypoints.apigw.middleware.auth import get_auth_context

# Create app
app = create_app(
    cors_allow_origin=CORS_ALLOW_ORIGIN,
    cors_max_age=CORS_MAX_AGE,
)

# Initialize use cases
get_dashboard_overview_uc = GetDashboardOverview()
get_events_stats_uc = GetEventsStats()
get_tasks_stats_uc = GetTasksStats()
get_users_stats_uc = GetUsersStats()


# API Routes
@app.get("/dashboard/overview")
def get_dashboard_overview(
    start_date: Annotated[int | None, Query] = None,
    end_date: Annotated[int | None, Query] = None,
):
    """
    Get dashboard overview endpoint.

    Returns aggregated statistics from events, tasks, and users.
    Requires authentication.
    """
    # Get auth context
    get_auth_context(app)

    # Execute use case
    result = get_dashboard_overview_uc.execute(start_date=start_date, end_date=end_date)

    # Return response
    return result.model_dump(), HTTPStatus.OK


@app.get("/dashboard/events-stats")
def get_events_stats(
    start_date: Annotated[int | None, Query] = None,
    end_date: Annotated[int | None, Query] = None,
):
    """
    Get events statistics endpoint.

    Returns event statistics aggregated by severity, account, region, and source.
    Requires authentication.
    """
    # Get auth context
    get_auth_context(app)

    # Execute use case
    result = get_events_stats_uc.execute(start_date=start_date, end_date=end_date)

    # Return response
    return result.model_dump(), HTTPStatus.OK


@app.get("/dashboard/tasks-stats")
def get_tasks_stats(
    start_date: Annotated[int | None, Query] = None,
    end_date: Annotated[int | None, Query] = None,
):
    """
    Get tasks statistics endpoint.

    Returns task statistics aggregated by status, priority, with overdue count.
    Requires authentication.
    """
    # Get auth context
    get_auth_context(app)

    # Execute use case
    result = get_tasks_stats_uc.execute(start_date=start_date, end_date=end_date)

    # Return response
    return result.model_dump(), HTTPStatus.OK


@app.get("/dashboard/users-stats")
def get_users_stats():
    """
    Get users statistics endpoint.

    Returns user statistics aggregated by role and activity.
    Requires admin role.
    """
    # Get auth context and check admin
    auth = get_auth_context(app)
    if not auth.is_admin():
        from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

        raise UnauthorizedError("Admin role required to view user statistics")

    # Execute use case
    result = get_users_stats_uc.execute()

    # Return response
    return result.model_dump(), HTTPStatus.OK


# Lambda handler
def handler(event: dict, context: LambdaContext) -> dict:
    """Lambda function handler for dashboard endpoints."""
    return app.resolve(event, context)
