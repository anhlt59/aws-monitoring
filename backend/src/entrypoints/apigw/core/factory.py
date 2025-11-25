import json
from http import HTTPStatus

from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig, Response
from aws_lambda_powertools.event_handler.middlewares import NextMiddleware
from pydantic import BaseModel, ValidationError

from src.adapters.auth.jwt import JWTService
from src.common.constants import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    JWT_SECRET_KEY,
)

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
        except Exception:
            # TODO: Log the exception, refactor response
            return Response(status_code=401, content_type="application/json", body="{}")

    result = next_middleware(app)

    return result


# Application factory
def create_app(
    cors_allow_origin: str = "*",
    cors_max_age: int = 3600,
) -> APIGatewayRestResolver:
    """Create and configure the API Gateway application."""
    cors_config = CORSConfig(allow_origin=cors_allow_origin, max_age=cors_max_age)
    app = APIGatewayRestResolver(cors=cors_config, enable_validation=True)

    # Apply middlewares
    app.use(middlewares=[auth_middleware])

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
