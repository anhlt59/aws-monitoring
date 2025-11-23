"""Refresh authentication token use case."""

from pydantic import Field

from src.adapters.auth.jwt import jwt_service
from src.adapters.db.repositories.user import UserRepository
from src.common.exceptions import UnauthorizedError
from src.common.models import BaseModel


class RefreshTokenDTO(BaseModel):
    """Data transfer object for token refresh."""

    refresh_token: str = Field(..., description="JWT refresh token")


class NewAccessTokenDTO(BaseModel):
    """Data transfer object for new access token."""

    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")


class RefreshAuthToken:
    """
    Use case for refreshing an access token using a refresh token.

    Validates the refresh token and generates a new access token.
    """

    def __init__(self, user_repository: UserRepository | None = None):
        """
        Initialize use case.

        Args:
            user_repository: User repository instance (defaults to new instance)
        """
        self.user_repository = user_repository or UserRepository()

    def execute(self, dto: RefreshTokenDTO) -> NewAccessTokenDTO:
        """
        Refresh access token using refresh token.

        Args:
            dto: Refresh token data

        Returns:
            NewAccessTokenDTO with new access token

        Raises:
            UnauthorizedError: If refresh token is invalid or user not found
        """
        # Verify refresh token
        payload = jwt_service.verify_token(dto.refresh_token, token_type="refresh")

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
        access_token = jwt_service.generate_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
            remember_me=False,
        )

        # Get expiration time
        expires_in = jwt_service.get_token_expiration(remember_me=False)

        return NewAccessTokenDTO(
            access_token=access_token,
            token_type="Bearer",
            expires_in=expires_in,
        )
