import os

# Common
SERVICE = os.getenv("SERVICE", "teligent")
STAGE = os.getenv("STAGE", "dev")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
LOG_EVENT = os.getenv("LOG_EVENT", "true").lower() == "true"

# AWS
AWS_DEFAULT_PROFILE = os.getenv("AWS_DEFAULT_PROFILE", "default")
# fmt: off
AWS_REGIONS = {"us-east-1", "us-east-2", "us-west-1", "us-west-2", "af-south-1", "ap-east-1", "ap-south-1", "ap-northeast-3", "ap-northeast-2", "ap-southeast-1", "ap-southeast-2", "ap-northeast-1", "ca-central-1", "cn-north-1", "cn-northwest-1", "eu-central-1", "eu-west-1", "eu-west-2", "eu-south-1", "eu-west-3", "eu-north-1", "me-south-1", "sa-east-1"}  # noqa
# fmt: on
DYNAMODB_ENDPOINT = os.getenv("AWS_ENDPOINT", "http://localhost:4566")
DYNAMODB_REGION = os.getenv("AWS_REGION", "us-east-1")
DYNAMODB_DEFAULT_QUERY_LIMIT = os.getenv("DYNAMODB_DEFAULT_QUERY_LIMIT", 50)
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "teligent-local")

# API
CORS_ALLOW_ORIGIN = os.getenv("CORS_ALLOW_ORIGIN", "*")
CORS_MAX_AGE = os.getenv("CORS_MAX_AGE", 3600)
