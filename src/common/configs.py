import os

# Common
SERVICE = os.getenv("SERVICE", "monitoring")
STAGE = os.getenv("STAGE", "dev")

# # Path & Directory
# BASE_DIR = Path(__file__).resolve().parent.parent.parent
# STATIC_DIR = BASE_DIR / "statics"
# TEMPLATE_DIR = STATIC_DIR / "templates"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
LOG_EVENT = os.getenv("LOG_EVENT", "true").lower() == "true"

# AWS
AWS_REGION = os.getenv("AWS_REGION")
AWS_ENDPOINT = "http://localhost:4566" if STAGE == "local" else None
# # DynamoDB
# AWS_DYNAMODB_DEFAULT_QUERY_LIMIT = os.getenv("AWS_DYNAMODB_DEFAULT_QUERY_LIMIT", 50)
# AWS_DYNAMODB_TABLE = os.getenv("AWS_DYNAMODB_TABLE", "monitoring-master-local")
# AWS_DYNAMODB_TTL = int(os.getenv("AWS_DYNAMODB_TTL", 604800))  # 7 days in seconds
#
# # API
# CORS_ALLOW_ORIGIN = os.getenv("CORS_ALLOW_ORIGIN", "*")
# CORS_MAX_AGE = os.getenv("CORS_MAX_AGE", 3600)
