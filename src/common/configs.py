import os

# Common
SERVICE = os.getenv("SERVICE", "monitoring")
STAGE = os.getenv("STAGE", "dev")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
LOG_EVENT = os.getenv("LOG_EVENT", "true").lower() == "true"

# AWS
AWS_REGION = os.getenv("AWS_REGION")
AWS_ENDPOINT = "http://localhost:4566" if STAGE == "local" else None
# DynamoDB
AWS_DYNAMODB_DEFAULT_QUERY_LIMIT = os.getenv("AWS_DYNAMODB_DEFAULT_QUERY_LIMIT", 50)
AWS_DYNAMODB_TABLE = os.getenv("AWS_DYNAMODB_TABLE", "monitoring-master-local")

# API
CORS_ALLOW_ORIGIN = os.getenv("CORS_ALLOW_ORIGIN", "*")
CORS_MAX_AGE = os.getenv("CORS_MAX_AGE", 3600)
