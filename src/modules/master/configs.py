import os
from pathlib import Path

# File & Directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
STATIC_DIR = BASE_DIR / "statics"
TEMPLATE_DIR = STATIC_DIR / "templates"

CW_ALARM_TEMPLATE_FILE = "cloudwatch_alarm.jinja"
CW_LOG_TEMPLATE_FILE = "cloudwatch_log.jinja"
GUARDDUTY_TEMPLATE_FILE = "guardduty.jinja"
HEALTH_TEMPLATE_FILE = "health.jinja"
CFN_TEMPLATE_FILE = "cfn_deployment.jinja"
REPORT_TEMPLATE_FILE = "daily_report.jinja"

# Webhook URLs
REPORT_WEBHOOK_URL = os.environ.get("REPORT_WEBHOOK_URL")
MONITORING_WEBHOOK_URL = os.environ.get("MONITORING_WEBHOOK_URL")
DEPLOYMENT_WEBHOOK_URL = os.environ.get("DEPLOYMENT_WEBHOOK_URL")

# TODO:
# 1. Restructure metadata
# 2. Load metadata from environment or database
METADATA = {
    "000000000000": "LocalStack",
    "746166211068": "CM",
    "728171922033": "Neos",
}
