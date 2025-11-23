"""Get user use case."""

from src.adapters.db.repositories.user import UserRepository
from src.common.exceptions import NotFoundError
from src.domain.models.user import UserProfile


class GetUser:
    """
    Use case for retrieving a user by ID.

    Returns user profile without sensitive information.
    """

    def __init__(self, user_repository: UserRepository | None = None):
        """
        Initialize use case.

        Args:
            user_repository: User repository instance
        """
        self.user_repository = user_repository or UserRepository()

    def execute(self, user_id: str) -> UserProfile:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            UserProfile without sensitive data

        Raises:
            NotFoundError: If user not found
        """
        user = self.user_repository.get(user_id)

        if not user:
            raise NotFoundError(f"User not found: {user_id}")

        # Convert to profile (excludes password_hash)
        return UserProfile.from_user(user)
