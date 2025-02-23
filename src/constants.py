import os

STAGE = os.getenv("STAGE", "local")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
LOG_FORMAT = "%(asctime)s <%(module)s.%(funcName)s:%(lineno)s> - %(levelname)s - %(message)s"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
PARSE_TIME_FORMAT = "%Y%m%d%H%M%S"
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 4))

DB_URI = "mysql+pymysql://{user}:{password}@{host}:{port}/{name}".format(
    **{
        "user": os.getenv("DB_USERNAME", "root"),
        "password": os.getenv("DB_PASSWORD", "12345678"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "3306"),
        "name": os.getenv("DB_DATABASE", "denaribots"),
    }
)
DB_DEFAULT_UPDATE_BATCH_SIZE = 50
DB_DEFAULT_INSERT_BATCH_SIZE = 100

# AWS
FUNCTION_NAME = os.getenv("FUNCTION_NAME")
AWS_REGION = os.getenv("REGION", "us-east-1")
AWS_ENDPOINT = "http://localhost:4566" if STAGE == "local" else None

# DYNAMODB
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", "denaribots-local")
DYNAMODB_DEFAULT_BATCH_SIZE = 25
DYNAMODB_DEFAULT_BATCH_DELAY = 0.05

# SES
SES_SENDER_ADDRESS = os.getenv("SES_SENDER_ADDRESS", "no-reply-local@denaribots.app")
SES_SENDER_NAME = f"DENARI BOTS <{SES_SENDER_ADDRESS}>"

# SQS
SQS_NOTIFICATION_URL = os.getenv("SQS_NOTIFICATION_URL")
SQS_MONITOR_123_URL = os.getenv("SQS_MONITOR_123_URL")
SQS_MONITOR_4_URL = os.getenv("SQS_MONITOR_4_URL")
SQS_MONITOR_5_URL = os.getenv("SQS_MONITOR_5_URL")
SQS_MONITOR_6_URL = os.getenv("SQS_MONITOR_6_URL")
SQS_MONITOR_7_URL = os.getenv("SQS_MONITOR_7_URL")
# https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-batch-api-actions.html
MESSAGE_BATCH_SIZE = 10

# S3
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_FIRMWARE_INFO_KEY = os.getenv("FIRMWARE_INFO_KEY", "devices/fw-info.csv")

# Soracom
SORACOM_ENDPOINT = os.getenv("SORACOM_ENDPOINT", "https://jp.api.soracom.io/v1")
SORACOM_AUTH_KEY_ID = os.getenv("SORACOM_AUTH_KEY_ID")
SORACOM_AUTH_KEY_SECRET = os.getenv("SORACOM_AUTH_KEY_SECRET")
SORACOM_REQUEST_TIMEOUT = int(os.getenv("SORACOM_REQUEST_TIMEOUT", 5))

# Firebase
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")
FIREBASE_TIME_OUT = 10  # seconds

# Others
COMPRESS_SIZE = 50

# Slack
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
