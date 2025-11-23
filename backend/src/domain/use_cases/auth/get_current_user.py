"""Get current user use case."""

from src.adapters.db.repositories.user import UserRepository
from src.common.exceptions import NotFoundError
from src.domain.models.user import UserProfile


class GetCurrentUser:
    """
    Use case for retrieving current user profile.

    Returns user profile without sensitive information (excludes password_hash).
    """

    def __init__(self, user_repository: UserRepository | None = None):
        """
        Initialize use case.

        Args:
            user_repository: User repository instance (defaults to new instance)
        """
        self.user_repository = user_repository or UserRepository()

    def execute(self, user_id: str) -> UserProfile:
        """
        Get current user profile.

        Args:
            user_id: User ID from JWT token

        Returns:
            UserProfile without sensitive information

        Raises:
            NotFoundError: If user not found
        """
        user = self.user_repository.get(user_id)

        if not user:
            raise NotFoundError(f"User not found: {user_id}")

        # Convert to profile (excludes password_hash)
        return UserProfile.from_user(user)
