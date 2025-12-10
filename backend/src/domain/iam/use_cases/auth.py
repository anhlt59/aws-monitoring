"""Auth use cases."""
from pydantic import BaseModel, Field
from werkzeug.security import check_password_hash

from src.adapters.db.repositories.user import UserRepository
from src.common.exceptions import UnauthorizedError, NotFoundError
from src.domain.models.user import User, UserProfile
from src.adapters.jwt import JWTService


# DTOs -----------------------------------
class AuthenticateUserDTO(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="Plain text password")


class AuthTokensDTO(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")


class AccessTokenDTO(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")


class LogoutUserDTO(BaseModel):
    access_token: str = Field(..., description="JWT access token to invalidate")


class RefreshTokenDTO(BaseModel):
    refresh_token: str = Field(..., description="JWT refresh token")


# Use Cases ------------------------------
class AuthUseCases:
    """Authentication use cases."""

    def __init__(self, user_repository: UserRepository, jwt_service: JWTService):
        self.user_repository = user_repository
        self.jwt_service = jwt_service

    def authenticate_user(self, dto: AuthenticateUserDTO) -> User:
        # Normalize email
        email = dto.email.lower().strip()

        try:
            # Find user by email
            user = self.user_repository.get_by_email(email)
        except Exception:
            # Don't reveal whether user exists (security best practice)
            raise UnauthorizedError("Invalid email or password")

        # Verify password
        if not check_password_hash(dto.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            raise UnauthorizedError("User account is inactive")

        return user

    def generate_auth_tokens(self, user: User) -> AuthTokensDTO:
        # Generate access token
        access_token = self.jwt_service.generate_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
        )

        # Generate refresh token
        refresh_token = self.jwt_service.generate_refresh_token(user_id=user.id)

        # Get expiration time
        expires_in = self.jwt_service.get_token_expiration()

        return AuthTokensDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",  # nosec
            expires_in=expires_in,
        )

    def get_current_user(self, user_id: str) -> UserProfile:
        if user := self.user_repository.get(user_id):
            return UserProfile.model_validate(user)

        raise NotFoundError(f"User not found: {user_id}")

    def logout_user(self, dto: LogoutUserDTO) -> bool:
        # TODO: Implement token blacklisting in DynamoDB if needed
        # For now, logout is handled client-side by removing the token
        return True

    def refresh_auth_token(self, dto: RefreshTokenDTO) -> AccessTokenDTO:
        # Verify refresh token
        payload = self.jwt_service.verify_token(dto.refresh_token, token_type="refresh")

        # Extract user ID
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError("Invalid refresh token: missing user ID")

        # Verify user still exists and is active
        user = self.user_repository.get(user_id)
        if not user:
            raise UnauthorizedError("User not found")

        if not user.is_active:
            raise UnauthorizedError("User account is inactive")

        # Generate new access token
        access_token = self.jwt_service.generate_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
        )

        # Get expiration time
        expires_in = self.jwt_service.get_token_expiration()

        return AccessTokenDTO(
            access_token=access_token,
            token_type="Bearer",
            expires_in=expires_in,
        )
