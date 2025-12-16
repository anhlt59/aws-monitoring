from pydantic import BaseModel, Field, field_validator

from src.common.models import PaginatedInputDTO, PaginatedOutputDTO
from src.domain.iam.models import UserProfile, UserRole


def _validate_email(value: str) -> str:
    value = value.lower().strip()
    if "@" not in value or "." not in value.split("@")[1]:
        raise ValueError("Invalid email format")
    return value


class AuthenticateUserDTO(BaseModel):
    email: str = Field(description="User email address")
    password: str = Field(description="Plain text password")


class AuthTokensDTO(BaseModel):
    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(description="Access token expiration time in seconds")


class AccessTokenDTO(BaseModel):
    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(description="Access token expiration time in seconds")


class LogoutUserDTO(BaseModel):
    access_token: str = Field(description="JWT access token to invalidate")


class RefreshTokenDTO(BaseModel):
    refresh_token: str = Field(description="JWT refresh token")


class ChangePasswordDTO(BaseModel):
    user_id: str = Field(description="User ID")
    current_password: str = Field(description="Current password")
    new_password: str = Field(min_length=8, description="New password")


class CreateUserDTO(BaseModel):
    email: str = Field(description="User email address")
    full_name: str = Field(min_length=2, max_length=100, description="User full name")
    password: str | None = Field(None, min_length=8, description="User password (auto-generated if not provided)")
    role: UserRole = Field(UserRole.USER, description="User role")

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return _validate_email(value)


class UpdateUserDTO(BaseModel):
    user_id: str = Field(description="User ID")
    email: str | None = Field(None, description="User email address")
    full_name: str | None = Field(None, min_length=2, max_length=100, description="User full name")

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        return _validate_email(value)


class ListUsersDTO(PaginatedInputDTO):
    role: UserRole | None = Field(None, description="Filter by role")


class PaginatedUsersDTO(PaginatedOutputDTO):
    items: list[UserProfile]
