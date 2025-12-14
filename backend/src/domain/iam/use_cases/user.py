from pydantic import BaseModel, Field, field_validator
from uuid_utils import uuid7
from werkzeug.security import generate_password_hash

from src.adapters.db.repositories.user import UserRepository
from src.common.exceptions import BadRequestError, ConflictError, NotFoundError, UnauthorizedError
from src.common.models import PaginatedInputDTO, PaginatedOutputDTO
from src.common.utils.datetime_utils import current_utc_timestamp
from src.domain.models.user import User, UserProfile, UserRole


# DTOs -----------------------------------
class ChangePasswordDTO(BaseModel):
    user_id: str = Field(..., description="User ID")
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class CreateUserDTO(BaseModel):
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


class ListUsersDTO(PaginatedInputDTO):
    role: UserRole | None = Field(None, description="Filter by role")
    email_startswith: str | None = Field(None, description="Search by email")


class PaginatedUsersDTO(PaginatedOutputDTO):
    items: list[UserProfile]


# Use Cases ------------------------------
class UserUseCases:
    """User use cases."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def change_password(self, dto: ChangePasswordDTO) -> bool:
        user = self.user_repository.get(dto.user_id)
        if not user:
            raise NotFoundError(f"User not found: {dto.user_id}")

        # Verify current password
        if not generate_password_hash(dto.current_password, user.password_hash):
            raise UnauthorizedError("Current password is incorrect")

        # Hash new password
        new_password_hash = generate_password_hash(dto.new_password)

        # Update password
        user.password_hash = new_password_hash
        user.updated_at = current_utc_timestamp()

        # Save user
        self.user_repository.update(user)

        return True

    def create_user(self, dto: CreateUserDTO) -> User:
        # Check email uniqueness
        try:
            existing_user = self.user_repository.get_by_email(dto.email)
            if existing_user:
                raise ConflictError(f"User with email {dto.email} already exists")
        except Exception as e:
            if isinstance(e, ConflictError):
                raise

        # Hash password
        password_hash = generate_password_hash(dto.password)

        # Create user entity
        user = User(
            id=str(uuid7()),
            email=dto.email,
            full_name=dto.full_name,
            password_hash=password_hash,
            role=dto.role,
        )

        # Save user
        self.user_repository.create(user)

        return user

    def delete_user(self, user_id: str, requesting_user_id: str) -> bool:
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

    def get_user(self, user_id: str) -> UserProfile:
        if user := self.user_repository.get(user_id):
            return UserProfile.model_validate(user)

        raise NotFoundError(f"User not found: {user_id}")

    def list_users(self, dto: ListUsersDTO) -> PaginatedUsersDTO:
        # Use repository methods based on filters
        if dto.role:
            users = self.user_repository.list_by_role(dto.role)
        else:
            users = self.user_repository.all()

        # Apply search filter
        if dto.search:
            search_term = dto.search.lower()
            users = [u for u in users if search_term in u.email.lower() or search_term in u.full_name.lower()]

        # Convert to profiles
        profiles = [UserProfile.from_user(u) for u in users]

        # Calculate pagination
        total = len(profiles)
        start_idx = (dto.page - 1) * dto.page_size
        end_idx = start_idx + dto.page_size
        paginated_profiles = profiles[start_idx:end_idx]
        has_more = end_idx < total

        return PaginatedUsersDTO(
            items=paginated_profiles,
        )
