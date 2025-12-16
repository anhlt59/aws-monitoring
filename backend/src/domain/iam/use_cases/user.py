from uuid_utils import uuid7
from werkzeug.security import generate_password_hash

from src.adapters.db.repositories import UserRepository
from src.common.exceptions import NotFoundError
from src.common.utils.datetime_utils import current_utc_timestamp

from ..dtos import ChangePasswordDTO, CreateUserDTO, ListUsersDTO, PaginatedUsersDTO, UpdateUserDTO
from ..exceptions import EmailDuplicateError, InvalidCredentialsError, SelfDeletionError, UserNotFoundError
from ..models import User, UserProfile


class UserUseCases:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def change_password(self, dto: ChangePasswordDTO) -> bool:
        user = self.user_repository.get(dto.user_id)
        if not user:
            raise UserNotFoundError(f"User not found: {dto.user_id}")

        # Verify current password
        if not generate_password_hash(dto.current_password, user.password_hash):
            raise InvalidCredentialsError("Current password is incorrect")

        # Hash new password
        new_password_hash = generate_password_hash(dto.new_password)

        # Update password
        user.password_hash = new_password_hash
        user.updated_at = current_utc_timestamp()

        # Save user
        self.user_repository.update(user)

        return True

    def update_user(self, dto: UpdateUserDTO):
        user = self.user_repository.get(dto.user_id)
        if not user:
            raise NotFoundError(f"User not found: {dto.user_id}")

        # Update fields
        if dto.email:
            # Check email uniqueness
            try:
                existing_user = self.user_repository.get_by_email(dto.email)
                if existing_user and existing_user.id != dto.user_id:
                    raise EmailDuplicateError(f"User with email {dto.email} already exists")
            except Exception as e:
                if isinstance(e, EmailDuplicateError):
                    raise

            user.email = dto.email

        if dto.full_name:
            user.full_name = dto.full_name

        user.updated_at = current_utc_timestamp()

        # Save user
        self.user_repository.update(user)

    def create_user(self, dto: CreateUserDTO) -> User:
        # Check email uniqueness
        try:
            existing_user = self.user_repository.get_by_email(dto.email)
            if existing_user:
                raise EmailDuplicateError(f"User with email {dto.email} already exists")
        except Exception as e:
            if isinstance(e, EmailDuplicateError):
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
            raise SelfDeletionError("Cannot delete your own account")

        # Verify user exists
        user = self.user_repository.get(user_id)
        if not user:
            raise UserNotFoundError(f"User not found: {user_id}")

        # Delete user
        self.user_repository.delete(user_id)

        return True

    def get_user(self, user_id: str) -> UserProfile:
        if user := self.user_repository.get(user_id):
            return UserProfile.model_validate(user)

        raise UserNotFoundError(f"User not found: {user_id}")

    def list_users(self, dto: ListUsersDTO) -> PaginatedUsersDTO:
        # Use repository methods based on filters
        if dto.role:
            results = self.user_repository.list_by_role(
                dto.role, direction=dto.direction, limit=dto.limit, cursor=dto.cursor
            )
        else:
            results = self.user_repository.all(direction=dto.direction, limit=dto.limit, cursor=dto.cursor)

        return PaginatedUsersDTO(
            items=results.items,
            limit=dto.limit,
            previous=dto.next,
            next=results.cursor,
        )
