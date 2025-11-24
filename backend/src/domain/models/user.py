"""User domain model and related enums."""

from enum import Enum

from pydantic import Field, field_validator

from src.common.models import BaseModel
from src.common.utils.datetime_utils import current_utc_timestamp


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(BaseModel):
    """
    User domain model for authentication and authorization.

    Represents a user in the AWS monitoring system with authentication
    and authorization capabilities.
    """

    # Identity
    id: str  # User UUID
    email: str
    full_name: str
    password_hash: str  # Bcrypt hashed password (never exposed in API)

    # Authorization
    role: UserRole = UserRole.USER

    # Timestamps
    created_at: int = Field(default_factory=current_utc_timestamp)
    updated_at: int = Field(default_factory=current_utc_timestamp)

    @property
    def persistence_id(self) -> str:
        """DynamoDB sort key for user."""
        return self.id

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """Validate email format."""
        value = value.lower().strip()
        if "@" not in value or "." not in value.split("@")[1]:
            raise ValueError("Invalid email format")
        return value

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        """Validate full name is not empty."""
        value = value.strip()
        if not value or len(value) < 2:
            raise ValueError("Full name must be at least 2 characters")
        if len(value) > 100:
            raise ValueError("Full name cannot exceed 100 characters")
        return value

    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN


class UserProfile(BaseModel):
    """
    User profile model for API responses.
    Excludes sensitive information like password_hash.
    """

    id: str
    email: str
    full_name: str
    role: UserRole
    created_at: int

    @classmethod
    def from_user(cls, user: User) -> "UserProfile":
        """Create profile from User entity."""
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            created_at=user.created_at,
        )
