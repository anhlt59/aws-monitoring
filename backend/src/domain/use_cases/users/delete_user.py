"""Delete user use case."""

from src.adapters.db.repositories.user import UserRepository
from src.common.exceptions import BadRequestError, NotFoundError


class DeleteUser:
    """
    Use case for deleting a user.

    Requires admin permissions.
    Prevents self-deletion.
    """

    def __init__(self, user_repository: UserRepository | None = None):
        """
        Initialize use case.

        Args:
            user_repository: User repository instance
        """
        self.user_repository = user_repository or UserRepository()

    def execute(self, user_id: str, requesting_user_id: str) -> bool:
        """
        Delete user by ID.

        Args:
            user_id: User ID to delete
            requesting_user_id: User ID making the request

        Returns:
            True if deleted successfully

        Raises:
            NotFoundError: If user not found
            BadRequestError: If trying to delete self
        """
        # Prevent self-deletion
        if user_id == requesting_user_id:
            raise BadRequestError("Cannot delete your own account")

        # Verify user exists
        user = self.user_repository.get(user_id)
        if not user:
            raise NotFoundError(f"User not found: {user_id}")

        # Delete user
        self.user_repository.delete(user_id)

        return True
