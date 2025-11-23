"""Logout user use case."""

from pydantic import Field

from src.common.models import BaseModel


class LogoutUserDTO(BaseModel):
    """Data transfer object for user logout."""

    access_token: str = Field(..., description="JWT access token to invalidate")


class LogoutUser:
    """
    Use case for logging out a user.

    Note: In a stateless JWT implementation, logout is handled client-side
    by removing the token. For server-side token blacklisting, you would
    need to store the token in a blacklist (e.g., DynamoDB with TTL).

    For now, this use case is a placeholder that always succeeds.
    In production, you might want to:
    1. Add token to blacklist in DynamoDB with TTL matching token expiration
    2. Check blacklist in JWT verification middleware
    """

    def execute(self, dto: LogoutUserDTO) -> bool:
        """
        Logout user by invalidating their access token.

        Args:
            dto: Logout data containing access token

        Returns:
            True if logout successful

        Note:
            In a stateless JWT system, this is primarily client-side.
            For server-side blacklisting, implement token storage in DynamoDB.
        """
        # TODO: Implement token blacklisting in DynamoDB if needed
        # For now, logout is handled client-side by removing the token
        return True
