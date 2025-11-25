import json
import os
from pathlib import Path

# File & Directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BASE_DIR / "statics"
TEMPLATE_DIR = STATIC_DIR / "templates"

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
AWS_DYNAMODB_TABLE = os.getenv("AWS_DYNAMODB_TABLE", "monitoring-local")
AWS_DYNAMODB_TTL = int(os.getenv("AWS_DYNAMODB_TTL", 604800))  # 7 days in seconds

# Webhook URLs
REPORT_WEBHOOK_URL = os.environ.get("REPORT_WEBHOOK_URL")
MONITORING_WEBHOOK_URL = os.environ.get("MONITORING_WEBHOOK_URL")
DEPLOYMENT_WEBHOOK_URL = os.environ.get("DEPLOYMENT_WEBHOOK_URL")

# Template files
CW_ALARM_TEMPLATE_FILE = "cloudwatch_alarm.jinja"
CW_LOG_TEMPLATE_FILE = "cloudwatch_log.jinja"
GUARDDUTY_TEMPLATE_FILE = "guardduty.jinja"
HEALTH_TEMPLATE_FILE = "health.jinja"
CFN_TEMPLATE_FILE = "cfn_deployment.jinja"
REPORT_TEMPLATE_FILE = "daily_report.jinja"

# Account Metadata
METADATA = json.loads(
    os.environ.get(
        "AWS_ACCOUNT_METADATA", '{"000000000000": "LocalStack", "746166211068": "CM", "728171922033": "Neos"}'
    )
)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30"))
