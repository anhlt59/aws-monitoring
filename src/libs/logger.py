import logging

from aws_lambda_powertools.logging import Logger, correlation_paths

from src.libs.configs import LOG_LEVEL, SERVICE

__all__ = ["logger", "correlation_paths"]

logger = Logger(level=LOG_LEVEL, service=SERVICE)

logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("boto3").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("pynamodb").setLevel(logging.WARNING)
