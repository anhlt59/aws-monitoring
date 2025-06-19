from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.common.configs import CORS_ALLOW_ORIGIN, CORS_MAX_AGE
from src.common.logger import correlation_paths, logger

cors_config = CORSConfig(allow_origin=CORS_ALLOW_ORIGIN, max_age=CORS_MAX_AGE)
app = APIGatewayRestResolver(cors=cors_config, enable_validation=True)


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
def handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
