from aws_lambda_powertools.utilities.typing import LambdaContext

from src.adapters.api.accounts import app
from src.common.logger import correlation_paths, logger


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
def handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
