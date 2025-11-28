"""Change password use case."""

from pydantic import Field

from src.adapters.auth.password import password_service
from src.adapters.db.repositories.user import UserRepository
from src.common.exceptions import NotFoundError, UnauthorizedError
from src.common.models import BaseModel
from src.common.utils.datetime_utils import current_utc_timestamp


class ChangePasswordDTO(BaseModel):
    """Data transfer object for changing password."""

    user_id: str = Field(..., description="User ID")
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class ChangePassword:
    """
    Use case for changing user password.

    Verifies current password before updating.
    """

    def __init__(self, user_repository: UserRepository | None = None):
        """
        Initialize use case.

        Args:
            user_repository: User repository instance
        """
        self.user_repository = user_repository or UserRepository()

    def execute(self, dto: ChangePasswordDTO) -> bool:
        """
        Change user password.

        Args:
            dto: Password change data

        Returns:
            True if password changed successfully

        Raises:
            NotFoundError: If user not found
            UnauthorizedError: If current password is incorrect
        """
        # Fetch user
        user = self.user_repository.get(dto.user_id)
        if not user:
            raise NotFoundError(f"User not found: {dto.user_id}")

        # Verify current password
        if not password_service.verify_password(dto.current_password, user.password_hash):
            raise UnauthorizedError("Current password is incorrect")

        # Hash new password
        new_password_hash = password_service.hash_password(dto.new_password)

        # Update password
        user.password_hash = new_password_hash
        user.updated_at = current_utc_timestamp()

        # Save user
        self.user_repository.update(user)

        return True
