"""JWT token management service."""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from src.common.constants import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    JWT_SECRET_KEY,
)
from src.common.exceptions import AuthenticationError


class JWTService:
    """Service for managing JWT tokens."""

    def __init__(
        self, secret_key: str, algorithm: str, access_token_expire_minutes: int, refresh_token_expire_days: int
    ):
        """Initialize JWT service with configuration from environment."""
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def generate_access_token(self, user_id: str, email: str, role: str, remember_me: bool = False) -> str:
        """
        Generate JWT access token.

        Args:
            user_id: User ID
            email: User email
            role: User role
            remember_me: If True, extend expiration to 30 days

        Returns:
            JWT token string
        """
        expire_minutes = self.refresh_token_expire_days * 24 * 60 if remember_me else self.access_token_expire_minutes
        expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)

        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "type": "access",
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def generate_refresh_token(self, user_id: str) -> str:
        """
        Generate JWT refresh token.

        Args:
            user_id: User ID

        Returns:
            JWT refresh token string
        """
        expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)

        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict[str, Any]:
        """
        Decode JWT token and return claims.

        Args:
            token: JWT token string

        Returns:
            Dictionary with token claims

        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except ExpiredSignatureError as e:
            raise AuthenticationError("Token has expired") from e
        except InvalidTokenError as e:
            raise AuthenticationError("Invalid token") from e

    def verify_token(self, token: str, token_type: str = "access") -> dict[str, Any]:
        """
        Verify JWT token and return claims if valid.

        Args:
            token: JWT token string
            token_type: Expected token type ("access" or "refresh")

        Returns:
            Dictionary with token claims

        Raises:
            AuthenticationError: If token is invalid, expired, or wrong type
        """
        payload = self.decode_token(token)

        # Verify token type
        if payload.get("type") != token_type:
            raise AuthenticationError(f"Invalid token type. Expected {token_type}")

        return payload

    def extract_user_id(self, token: str) -> str:
        """
        Extract user ID from token.

        Args:
            token: JWT token string

        Returns:
            User ID

        Raises:
            AuthenticationError: If token is invalid or expired
        """
        payload = self.verify_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise AuthenticationError("Token does not contain user ID")

        return user_id

    def get_token_expiration(self, remember_me: bool = False) -> int:
        """
        Get token expiration time in seconds.

        Args:
            remember_me: If True, return extended expiration

        Returns:
            Expiration time in seconds
        """
        if remember_me:
            return self.refresh_token_expire_days * 24 * 60 * 60
        return self.access_token_expire_minutes * 60


jwt_service = JWTService(
    secret_key=JWT_SECRET_KEY,
    algorithm=JWT_ALGORITHM,
    access_token_expire_minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    refresh_token_expire_days=JWT_REFRESH_TOKEN_EXPIRE_DAYS,
)
