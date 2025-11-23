"""Password hashing and verification service."""

import os

from passlib.context import CryptContext


class PasswordService:
    """Service for password hashing and verification using bcrypt."""

    def __init__(self):
        """Initialize password service with bcrypt configuration."""
        bcrypt_rounds = int(os.getenv("BCRYPT_ROUNDS", "12"))

        # Create password context with bcrypt
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=bcrypt_rounds,
        )

    def hash_password(self, plain_password: str) -> str:
        """
        Hash a plain text password using bcrypt.

        Args:
            plain_password: Plain text password

        Returns:
            Hashed password string
        """
        return self.pwd_context.hash(plain_password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hashed password.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to verify against

        Returns:
            True if password matches, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def needs_rehash(self, hashed_password: str) -> bool:
        """
        Check if a password hash needs to be updated.

        This is useful when changing bcrypt rounds or algorithms.

        Args:
            hashed_password: Hashed password to check

        Returns:
            True if hash needs update, False otherwise
        """
        return self.pwd_context.needs_update(hashed_password)


# Singleton instance
password_service = PasswordService()
