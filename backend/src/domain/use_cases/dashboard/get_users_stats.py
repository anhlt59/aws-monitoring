"""Get users statistics use case."""

from collections import defaultdict
from pydantic import Field

from src.adapters.db.repositories.user import UserRepository
from src.common.models import BaseModel
from src.common.utils.datetime_utils import current_utc_timestamp


class UsersStatsDTO(BaseModel):
    """Users statistics response."""

    total: int = Field(..., description="Total number of users")
    by_role: dict[str, int] = Field(..., description="Count by role")
    active_users: int = Field(..., description="Number of active users (logged in last 30 days)")
    inactive_users: int = Field(..., description="Number of inactive users")


class GetUsersStats:
    """
    Use case for retrieving users statistics.

    Aggregates user data by role and activity.
    Requires admin permissions.
    """

    def __init__(self, user_repository: UserRepository | None = None):
        """
        Initialize use case.

        Args:
            user_repository: User repository instance
        """
        self.user_repository = user_repository or UserRepository()

    def execute(self) -> UsersStatsDTO:
        """
        Get users statistics.

        Returns:
            UsersStatsDTO with aggregated statistics
        """
        # Get all users
        users = self.user_repository.list_all()

        # Initialize counters
        by_role = defaultdict(int)
        active_count = 0

        # Calculate 30 days ago timestamp
        thirty_days_ago = current_utc_timestamp() - (30 * 24 * 60 * 60)

        # Aggregate statistics
        for user in users:
            by_role[user.role.value] += 1

            # Count active users (logged in within last 30 days)
            if user.last_login and user.last_login >= thirty_days_ago:
                active_count += 1

        total_users = len(users)
        inactive_count = total_users - active_count

        return UsersStatsDTO(
            total=total_users,
            by_role=dict(by_role),
            active_users=active_count,
            inactive_users=inactive_count,
        )
