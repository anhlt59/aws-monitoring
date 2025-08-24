import json
from http import HTTPStatus

from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig, Response
from pydantic import ValidationError


def create_app(cors_allow_origin: str = "*", cors_max_age: int = 3600) -> APIGatewayRestResolver:
    """Create and configure the API Gateway application."""
    cors_config = CORSConfig(allow_origin=cors_allow_origin, max_age=cors_max_age)
    app = APIGatewayRestResolver(cors=cors_config, enable_validation=True)

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
