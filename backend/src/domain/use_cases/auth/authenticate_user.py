"""Authenticate user use case."""

from pydantic import BaseModel, Field

from src.adapters.auth.password import password_service
from src.adapters.db.repositories.user import UserRepository
from src.common.exceptions import UnauthorizedError
from src.domain.models.user import User


class AuthenticateUserDTO(BaseModel):
    """Data transfer object for user authentication."""

    email: str = Field(..., description="User email address")
    password: str = Field(..., description="Plain text password")


class AuthenticateUser:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

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

        return user
