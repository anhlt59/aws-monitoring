from http import HTTPStatus

from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    RequestEntityTooLargeError,
    RequestTimeoutError,
    ServiceError,
    ServiceUnavailableError,
    UnauthorizedError,
)
from pydantic_core._pydantic_core import ValidationError


class UnprocessedError(ServiceError):
    """Unprocessed Error (422)"""

    def __init__(self, msg: str):
        super().__init__(HTTPStatus.UNPROCESSABLE_ENTITY, msg)


class ConflictError(ServiceError):
    """Conflict Error (409)"""

    def __init__(self, msg: str):
        super().__init__(HTTPStatus.CONFLICT, msg)


class AWSClientException(InternalServerError):
    pass


class AuthenticationError(Exception):
    """Authentication error for JWT and password verification."""

    pass


__all__ = [
    "BadRequestError",
    "ForbiddenError",
    "InternalServerError",
    "NotFoundError",
    "RequestEntityTooLargeError",
    "RequestTimeoutError",
    "ServiceError",
    "ServiceUnavailableError",
    "UnauthorizedError",
    "UnprocessedError",
    "ConflictError",
    "ValidationError",
    "AWSClientException",
    "AuthenticationError",
]
