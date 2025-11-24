"""Authentication middleware and decorators."""

import functools
from typing import Callable

from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

from src.adapters.auth.jwt import jwt_service
from src.common.exceptions import AuthenticationError


class AuthContext:
    """Authentication context attached to request."""

    def __init__(self, user_id: str, email: str, role: str):
        """
        Initialize authentication context.

        Args:
            user_id: Authenticated user ID
            email: User email
            role: User role
        """
        self.user_id = user_id
        self.email = email
        self.role = role

    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == "admin"

    def has_role(self, required_role: str) -> bool:
        """
        Check if user has the required role.

        Args:
            required_role: Required role

        Returns:
            True if user has the role
        """
        return self.role == required_role


def extract_token_from_header(app: APIGatewayRestResolver) -> str | None:
    """
    Extract JWT token from Authorization header.

    Args:
        app: API Gateway resolver app

    Returns:
        JWT token or None if not present

    Raises:
        UnauthorizedError: If Authorization header format is invalid
    """
    auth_header = app.current_event.headers.get("Authorization")

    if not auth_header:
        return None

    # Check for Bearer token format
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedError("Invalid Authorization header format. Expected: Bearer <token>")

    return parts[1]


def get_auth_context(app: APIGatewayRestResolver) -> AuthContext:
    """
    Get authentication context from current request.

    Args:
        app: API Gateway resolver app

    Returns:
        AuthContext with user information

    Raises:
        UnauthorizedError: If not authenticated or token invalid
    """
    # Check if auth context already exists in app context
    if hasattr(app, "_auth_context"):
        return app._auth_context

    # Extract and verify token
    token = extract_token_from_header(app)
    if not token:
        raise UnauthorizedError("Missing authorization token")

    try:
        # Verify and decode token
        payload = jwt_service.verify_token(token, token_type="access")  # nosec

        # Create auth context
        auth_context = AuthContext(
            user_id=payload["sub"],
            email=payload["email"],
            role=payload["role"],
        )

        # Cache in app context for the request
        app._auth_context = auth_context

        return auth_context

    except AuthenticationError as e:
        raise UnauthorizedError(str(e)) from e


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


def require_role(*allowed_roles: str) -> Callable:
    """
    Decorator to require specific role(s) for an endpoint.

    Usage:
        @app.get("/admin")
        @require_role("admin")
        def admin_endpoint():
            return {"message": "Admin only"}

        @app.get("/moderator")
        @require_role("admin", "moderator")
        def moderator_endpoint():
            return {"message": "Admin or moderator"}

    Args:
        *allowed_roles: Allowed role names

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get app instance
            app = None
            for arg in args:
                if isinstance(arg, APIGatewayRestResolver):
                    app = arg
                    break

            if not app:
                import inspect

                frame = inspect.currentframe()
                try:
                    if frame and frame.f_back:
                        app = frame.f_back.f_locals.get("app")
                finally:
                    del frame

            if not app:
                raise RuntimeError("Could not find APIGatewayRestResolver instance")

            # Get auth context (will raise if not authenticated)
            auth = get_auth_context(app)

            # Check role
            if auth.role not in allowed_roles:
                raise UnauthorizedError(f"Insufficient permissions. Required role: {' or '.join(allowed_roles)}")

            # Call original function
            return func(*args, **kwargs)

        return wrapper

    return decorator


def verify_user_or_admin(app: APIGatewayRestResolver, user_id: str) -> None:
    """
    Verify that the authenticated user is either the target user or an admin.

    Args:
        app: API Gateway resolver app
        user_id: Target user ID

    Raises:
        UnauthorizedError: If user is neither the target user nor an admin
    """
    auth = get_auth_context(app)

    if auth.user_id != user_id and not auth.is_admin():
        raise UnauthorizedError("Insufficient permissions. You can only access your own resources.")
