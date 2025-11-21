"""User domain model and related enums."""

from enum import Enum

from pydantic import Field, field_validator

from backend.src.common.models import BaseModel
from backend.src.common.utils.datetime_utils import current_utc_timestamp


class UserRole(str, Enum):
    """User role enumeration with permission hierarchy."""

    ADMIN = "admin"
    MANAGER = "manager"
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
    is_active: bool = True

    # Timestamps
    created_at: int = Field(default_factory=current_utc_timestamp)
    updated_at: int = Field(default_factory=current_utc_timestamp)
    last_login: int | None = None  # Unix timestamp of last login

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

    def has_permission(self, required_role: UserRole) -> bool:
        """
        Check if user has required permission level.

        Permission hierarchy: admin > manager > user
        """
        role_hierarchy = {
            UserRole.ADMIN: 3,
            UserRole.MANAGER: 2,
            UserRole.USER: 1,
        }
        return role_hierarchy[self.role] >= role_hierarchy[required_role]

    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN

    def is_manager_or_above(self) -> bool:
        """Check if user is manager or admin."""
        return self.role in (UserRole.ADMIN, UserRole.MANAGER)

    def update_last_login(self) -> None:
        """Update last login timestamp to current time."""
        self.last_login = current_utc_timestamp()
        self.updated_at = current_utc_timestamp()


class UserProfile(BaseModel):
    """
    User profile model for API responses.

    Excludes sensitive information like password_hash.
    """

    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: int
    last_login: int | None = None
    permissions: list[str] = []  # Computed based on role

    @classmethod
    def from_user(cls, user: User) -> "UserProfile":
        """Create profile from User entity."""
        permissions = cls._get_permissions_for_role(user.role)
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login,
            permissions=permissions,
        )

    @staticmethod
    def _get_permissions_for_role(role: UserRole) -> list[str]:
        """Get permissions based on role."""
        base_permissions = [
            "read:events",
            "read:own_tasks",
            "update:own_tasks",
            "read:own_profile",
            "update:own_profile",
        ]

        manager_permissions = [
            "read:all_tasks",
            "create:tasks",
            "update:tasks",
            "delete:own_tasks",
            "read:users",
        ]

        admin_permissions = [
            "create:users",
            "update:users",
            "delete:users",
            "delete:events",
            "delete:tasks",
            "read:config",
            "update:config",
        ]

        if role == UserRole.ADMIN:
            return base_permissions + manager_permissions + admin_permissions
        elif role == UserRole.MANAGER:
            return base_permissions + manager_permissions
        else:
            return base_permissions
