import os

import boto3

os.environ["QUERY_STRING"] = """fields @message, @log, @logStream
| filter @message like /(?i)(error|fail|exception)/
| sort @timestamp desc
| limit 200"""

boto3.setup_default_session(profile_name="lc-stg", region_name="ap-northeast-1")


if __name__ == "__main__":
    from src.handlers.agent.query_error_logs.main import handler

    handler(None, None)
