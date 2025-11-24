"""JWT token management service."""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from src.common.exceptions import UnauthorizedError


class JWTService:
    def __init__(
        self, secret_key: str, algorithm: str, access_token_expire_minutes: int, refresh_token_expire_days: int
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def generate_access_token(self, user_id: str, email: str, role: str, remember_me: bool = False) -> str:
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
        expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)

        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except ExpiredSignatureError as e:
            raise UnauthorizedError("Token has expired") from e
        except InvalidTokenError as e:
            raise UnauthorizedError("Invalid token") from e

    def verify_token(self, token: str, token_type: str = "access") -> dict[str, Any]:
        payload = self.decode_token(token)

        # Verify token type
        if payload.get("type") != token_type:
            raise UnauthorizedError(f"Invalid token type. Expected {token_type}")

        return payload

    def get_token_expiration(self, remember_me: bool = False) -> int:
        if remember_me:
            return self.refresh_token_expire_days * 24 * 60 * 60
        return self.access_token_expire_minutes * 60
