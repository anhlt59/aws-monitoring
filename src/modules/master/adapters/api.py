import json
from http import HTTPStatus

from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig, Response
from pydantic import ValidationError

from src.common.configs import CORS_ALLOW_ORIGIN, CORS_MAX_AGE

cors_config = CORSConfig(allow_origin=CORS_ALLOW_ORIGIN, max_age=CORS_MAX_AGE)
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
