import json
from http import HTTPStatus

from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig, Response
from aws_lambda_powertools.event_handler.middlewares import NextMiddleware
from pydantic import ValidationError


# Middlewares
def auth_middleware(app: APIGatewayRestResolver, next_middleware: NextMiddleware) -> Response:
    app.current_event.headers.get("Authorization")
    # return Response(status_code=401, content_type="application/json", body="{}")

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
