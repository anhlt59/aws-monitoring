
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError
from aws_lambda_powertools.event_handler.middlewares import NextMiddleware

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


# Middlewares
def auth_middleware(app: APIGatewayRestResolver, next_middleware: NextMiddleware) -> Response:
    if token := app.current_event.headers.get("Authorization"):
        try:
            # Verify and decode token
            payload = jwt_service.verify_token(token, token_type="access")  # nosec

            # Create auth context
            auth_context = AuthContext(
                user_id=payload.get("sub"),
                email=payload.get("email"),
                role=payload.get("role"),
            )

            # Cache in app context for the request
            app._auth_context = auth_context

            return auth_context

        except Exception as e:
            raise UnauthorizedError(str(e)) from e

        # return Response(status_code=401, content_type="application/json", body="{}")
    result = next_middleware(app)

    return result
