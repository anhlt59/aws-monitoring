"""Create user use case."""

from uuid_utils import uuid7
from pydantic import Field, field_validator

from src.adapters.auth.password import password_service
from src.adapters.db.repositories.user import UserRepository
from src.common.exceptions import ConflictError
from src.common.models import BaseModel
from src.domain.models.user import User, UserRole


class CreateUserDTO(BaseModel):
    """Data transfer object for creating user."""

    email: str = Field(..., description="User email address")
    full_name: str = Field(..., min_length=2, max_length=100, description="User full name")
    password: str | None = Field(None, min_length=8, description="User password (auto-generated if not provided)")
    role: UserRole = Field(UserRole.USER, description="User role")

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """Validate and normalize email."""
        value = value.lower().strip()
        if "@" not in value or "." not in value.split("@")[1]:
            raise ValueError("Invalid email format")
        return value


class CreateUser:
    """
    Use case for creating a new user.

    Validates email uniqueness and hashes password.
    Requires admin permissions.
    """

    def __init__(self, user_repository: UserRepository | None = None):
        """
        Initialize use case.

        Args:
            user_repository: User repository instance
        """
        self.user_repository = user_repository or UserRepository()

    def execute(self, dto: CreateUserDTO) -> User:
        """
        Create a new user.

        Args:
            dto: User creation data

        Returns:
            Created User entity

        Raises:
            ConflictError: If email already exists
        """
        # Check email uniqueness
        try:
            existing_user = self.user_repository.get_by_email(dto.email)
            if existing_user:
                raise ConflictError(f"User with email {dto.email} already exists")
        except Exception as e:
            if not isinstance(e, ConflictError):
                # Email doesn't exist, continue
                pass
            else:
                raise

        # Generate password if not provided
        import secrets

        password = dto.password or secrets.token_urlsafe(16)

        # Hash password
        password_hash = password_service.hash_password(password)

        # Create user entity
        user = User(
            id=str(uuid7()),
            email=dto.email,
            full_name=dto.full_name,
            password_hash=password_hash,
            role=dto.role,
            is_active=True,
        )

        # Save user
        self.user_repository.create(user)

        return user
