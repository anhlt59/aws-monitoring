"""Authentication middleware and decorators."""

import functools
import inspect
import json
from http import HTTPStatus
from typing import Callable

from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig, Response
from pydantic import BaseModel, ValidationError

from src.adapters.jwt import JWTService
from src.common.constants import (
    CORS_ALLOW_ORIGIN,
    CORS_MAX_AGE,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    JWT_SECRET_KEY,
)
from src.common.exceptions import UnauthorizedError

__all__ = ["login_required", "admin_required", "create_app", "jwt_service"]

jwt_service = JWTService(
    secret_key=JWT_SECRET_KEY,
    algorithm=JWT_ALGORITHM,
    access_token_expire_minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    refresh_token_expire_days=JWT_REFRESH_TOKEN_EXPIRE_DAYS,
)


class AuthContext(BaseModel):
    user_id: str
    email: str
    role: str

    def is_admin(self) -> bool:
        return self.role == "admin"


class APIGateway(APIGatewayRestResolver):
    _auth_context: AuthContext | None

    @property
    def auth_context(self) -> AuthContext | None:
        return self._auth_context

    @auth_context.setter
    def auth_context(self, value: AuthContext) -> None:
        self._auth_context = value


def _inspect_app(*args, **kwargs) -> APIGateway:
    # Get app instance from args (first positional argument is typically 'self' or app)
    for arg in args:
        if isinstance(arg, APIGateway):
            return arg
    # Try to get from function's global context
    frame = inspect.currentframe()
    try:
        if frame and frame.f_back:
            return frame.f_back.f_locals.get("app")
    finally:
        del frame

    raise RuntimeError("Could not find APIGatewayRestResolver instance")


# Decorator to get auth context
def login_required(func: Callable) -> Callable:
    """Decorator to require authentication for an endpoint."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        app = _inspect_app(*args, **kwargs)
        # Verify authentication
        if token := app.current_event.headers.get("Authorization"):
            payload = jwt_service.verify_token(token, token_type="access")  # nosec
            app.auth_context = AuthContext(
                user_id=payload.get("sub"),
                email=payload.get("email"),
                role=payload.get("role"),
            )
            # Call original function
            return func(*args, **kwargs)
        raise UnauthorizedError("Authentication required")

    return wrapper


def admin_required(func: Callable) -> Callable:
    """Decorator to require admin authentication for an endpoint."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        app = _inspect_app(*args, **kwargs)
        # Verify authentication
        if token := app.current_event.headers.get("Authorization"):
            payload = jwt_service.verify_token(token, token_type="access")  # nosec

            if payload.get("role") == "admin":
                app.auth_context = AuthContext(
                    user_id=payload.get("sub"),
                    email=payload.get("email"),
                    role=payload.get("role"),
                )
                # Call original function
                return func(*args, **kwargs)
        raise UnauthorizedError("Admin authentication required")

    return wrapper


def create_app(cors_allow_origin: str = CORS_ALLOW_ORIGIN, cors_max_age: int = CORS_MAX_AGE) -> APIGateway:
    """Create and configure the API Gateway application."""
    cors_config = CORSConfig(allow_origin=cors_allow_origin, max_age=cors_max_age)
    app = APIGateway(cors=cors_config, enable_validation=True)

    # Exception handlers
    @app.exception_handler(ValidationError)
    def handle_validation_error(ex: ValidationError):
        body = {
            "errors": ex.errors(),
            "message": "Validation Error",
        }
        return Response(
            status_code=HTTPStatus.BAD_REQUEST,
            body=json.dumps(body),
        )

    return app
