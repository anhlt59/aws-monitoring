from aws_lambda_powertools.event_handler import CORSConfig

from src.common.configs import CORS_ALLOW_ORIGIN, CORS_MAX_AGE

cors_config = CORSConfig(allow_origin=CORS_ALLOW_ORIGIN, max_age=CORS_MAX_AGE)
