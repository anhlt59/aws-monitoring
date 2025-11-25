"""User domain model and related enums."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

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

    id: str  # User UUID
    email: str
    full_name: str
    password_hash: str  # Bcrypt hashed password (never exposed in API)
    role: UserRole = UserRole.USER
    created_at: int = Field(default_factory=current_utc_timestamp)
    updated_at: int = Field(default_factory=current_utc_timestamp)

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

    model_config = ConfigDict(from_attributes=True)
