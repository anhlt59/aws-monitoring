"""Authenticate user use case."""

from pydantic import Field

from src.adapters.auth.password import password_service
from src.adapters.db.repositories.user import UserRepository
from src.common.exceptions import UnauthorizedError
from src.common.models import BaseModel
from src.domain.models.user import User


class AuthenticateUserDTO(BaseModel):
    """Data transfer object for user authentication."""

    email: str = Field(..., description="User email address")
    password: str = Field(..., description="Plain text password")


class AuthenticateUser:
    """
    Use case for authenticating a user with email and password.

    Returns the authenticated User entity if credentials are valid.
    """

    def __init__(self, user_repository: UserRepository | None = None):
        """
        Initialize use case.

        Args:
            user_repository: User repository instance (defaults to new instance)
        """
        self.user_repository = user_repository or UserRepository()

    def execute(self, dto: AuthenticateUserDTO) -> User:
        """
        Authenticate user with email and password.

        Args:
            dto: Authentication data (email and password)

        Returns:
            Authenticated User entity

        Raises:
            UnauthorizedError: If credentials are invalid or user not found
        """
        # Normalize email
        email = dto.email.lower().strip()

        try:
            # Find user by email
            user = self.user_repository.get_by_email(email)
        except Exception:
            # Don't reveal whether user exists (security best practice)
            raise UnauthorizedError("Invalid email or password")

        # Verify password
        if not password_service.verify_password(dto.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            raise UnauthorizedError("User account is inactive")

        # Update last login
        user.update_last_login()
        self.user_repository.update(user)

        return user
