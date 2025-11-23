"""Update user use case."""

from pydantic import Field, field_validator

from src.adapters.db.repositories.user import UserRepository
from src.common.exceptions import ConflictError, NotFoundError
from src.common.models import BaseModel
from src.common.utils.datetime_utils import current_utc_timestamp
from src.domain.models.user import User, UserRole


class UpdateUserDTO(BaseModel):
    """Data transfer object for updating user."""

    user_id: str = Field(..., description="User ID to update")
    email: str | None = Field(None, description="User email address")
    full_name: str | None = Field(None, min_length=2, max_length=100, description="User full name")
    role: UserRole | None = Field(None, description="User role")

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        """Validate and normalize email."""
        if value is None:
            return None
        value = value.lower().strip()
        if "@" not in value or "." not in value.split("@")[1]:
            raise ValueError("Invalid email format")
        return value


class UpdateUser:
    """
    Use case for updating user information.

    Validates email uniqueness if email is changed.
    Users can update their own profile, admins can update any user.
    """

    def __init__(self, user_repository: UserRepository | None = None):
        """
        Initialize use case.

        Args:
            user_repository: User repository instance
        """
        self.user_repository = user_repository or UserRepository()

    def execute(self, dto: UpdateUserDTO) -> User:
        """
        Update user information.

        Args:
            dto: Update data

        Returns:
            Updated User entity

        Raises:
            NotFoundError: If user not found
            ConflictError: If new email already exists
        """
        # Fetch existing user
        user = self.user_repository.get(dto.user_id)
        if not user:
            raise NotFoundError(f"User not found: {dto.user_id}")

        # Update email if provided
        if dto.email is not None and dto.email != user.email:
            # Check email uniqueness
            try:
                existing_user = self.user_repository.get_by_email(dto.email)
                if existing_user and existing_user.id != user.id:
                    raise ConflictError(f"User with email {dto.email} already exists")
            except NotFoundError:
                # Email doesn't exist, safe to use
                pass

            user.email = dto.email

        # Update full name if provided
        if dto.full_name is not None:
            user.full_name = dto.full_name

        # Update role if provided
        if dto.role is not None:
            user.role = dto.role

        # Update timestamp
        user.updated_at = current_utc_timestamp()

        # Save user
        self.user_repository.update(user)

        return user
