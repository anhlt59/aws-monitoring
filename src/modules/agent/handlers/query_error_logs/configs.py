import os

CW_INSIGHTS_QUERY_STRING = os.getenv(
    "CW_INSIGHTS_QUERY_STRING",
    "fields @message, @log, @logStream | filter @message like /(?i)(error|fail|exception)/ | sort @timestamp desc | limit 200",
)
CW_INSIGHTS_QUERY_DURATION = int(os.getenv("CW_INSIGHTS_QUERY_DURATION", 300))  # seconds
CW_LOGS_DELIVERY_LATENCY = int(os.getenv("CW_LOGS_DELIVERY_LATENCY", 15))  # seconds
CW_INSIGHTS_QUERY_DELAY = int(os.getenv("CW_INSIGHTS_QUERY_DELAY", 1))  # seconds
CW_INSIGHTS_QUERY_TIMEOUT = int(os.getenv("CW_INSIGHTS_QUERY_TIMEOUT", 15))  # seconds
CW_LOG_GROUPS_CHUNK_SIZE = int(os.getenv("CW_LOG_GROUPS_CHUNK_SIZE", 10))  # limit for log groups per query
