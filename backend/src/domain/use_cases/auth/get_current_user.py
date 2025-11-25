"""Get current user use case."""

from src.adapters.db.repositories.user import UserRepository
from src.common.exceptions import NotFoundError
from src.domain.models.user import UserProfile


class GetCurrentUser:
    def __init__(self, user_repository: UserRepository | None = None):
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

        if user := self.user_repository.get(user_id):
            # Convert to profile (excludes password_hash)
            return UserProfile.model_validate(user)

        raise NotFoundError(f"User not found: {user_id}")
