"""Authentication middleware and decorators."""
import functools
from typing import Callable

from pydantic import BaseModel

from src.adapters.auth.jwt import JWTService
from src.common.constants import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    JWT_SECRET_KEY,
)
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig, Response
from src.common.exceptions import UnauthorizedError
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator

jwt_service = JWTService(
    secret_key=JWT_SECRET_KEY,
    algorithm=JWT_ALGORITHM,
    access_token_expire_minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    refresh_token_expire_days=JWT_REFRESH_TOKEN_EXPIRE_DAYS,
)


class UserContext(BaseModel):
    # Authentication context attached to request, that obtains from JWT token
    user_id: str | None = None
    email: str | None = None
    role: str | None = None

    def is_admin(self) -> bool:
        return self.role == "admin"

    def is_anonymous(self) -> bool:
        return self.user_id is None

def get_auth_context(app: APIGatewayRestResolver) -> UserContext:

# Middlewares
def auth_middleware(app: APIGatewayRestResolver, next_middleware: NextMiddleware) -> Response:
    if token := app.current_event.headers.get("Authorization"):
        try:
            # Verify and decode token
            payload = jwt_service.verify_token(token, token_type="access")  # nosec

            # Create auth context
            user_context = UserContext(
                user_id=payload.get("sub"),
                email=payload.get("email"),
                role=payload.get("role"),
            )

            # Cache in app context for the request
            app.append_context(user=user_context)

        except Exception as e:
            # TODO: Log the exception, refactor response
            raise UnauthorizedError(str(e)) from e

    result = next_middleware(app)

    return result

# Decorator to get auth context
def require_auth(func: Callable) -> Callable:
    """
    Decorator to require authentication for an endpoint.

    The authenticated user context will be available via get_auth_context(app).

    Usage:
        @app.get("/protected")
        @require_auth
        def protected_endpoint():
            auth = get_auth_context(app)
            return {"user_id": auth.user_id}

    Args:
        func: Handler function to decorate

    Returns:
        Decorated function that requires authentication
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get app instance from args (first positional argument is typically 'self' or app)
        app = None
        for arg in args:
            if isinstance(arg, APIGatewayRestResolver):
                app = arg
                break

        if not app:
            # Try to get from function's global context
            import inspect

            frame = inspect.currentframe()
            try:
                if frame and frame.f_back:
                    app = frame.f_back.f_locals.get("app")
            finally:
                del frame

        if not app:
            raise RuntimeError("Could not find APIGatewayRestResolver instance")

        # Verify authentication
        get_auth_context(app)

        # Call original function
        return func(*args, **kwargs)

    return wrapper
