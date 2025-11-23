"""Generate authentication tokens use case."""

from pydantic import Field

from src.adapters.auth.jwt import jwt_service
from src.common.models import BaseModel
from src.domain.models.user import User


class AuthTokensDTO(BaseModel):
    """Data transfer object for authentication tokens."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")


class GenerateAuthTokens:
    """
    Use case for generating JWT authentication tokens.

    Generates both access and refresh tokens for an authenticated user.
    """

    def execute(self, user: User, remember_me: bool = False) -> AuthTokensDTO:
        """
        Generate authentication tokens for user.

        Args:
            user: Authenticated user entity
            remember_me: If True, extends token expiration to 30 days

        Returns:
            AuthTokensDTO with access and refresh tokens
        """
        # Generate access token
        access_token = jwt_service.generate_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
            remember_me=remember_me,
        )

        # Generate refresh token
        refresh_token = jwt_service.generate_refresh_token(user_id=user.id)

        # Get expiration time
        expires_in = jwt_service.get_token_expiration(remember_me=remember_me)

        return AuthTokensDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=expires_in,
        )
