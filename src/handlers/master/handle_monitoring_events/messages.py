import os

from src.adapters.aws.data_classes import (
    CwAlarmEvent,
    GuardDutyFindingEvent,
    HealthEvent,
)
from src.adapters.db import EventRepository
from src.adapters.notifiers import SlackNotifier, render_message

CW_ALARM_TEMPLATE_FILE = "slack_messages/cloudwatch_alarm.json"
CW_LOG_TEMPLATE_FILE = "slack_messages/cloudwatch_log.json"
GUARDDUTY_TEMPLATE_FILE = "slack_messages/guardduty.json"
HEALTH_TEMPLATE_FILE = "slack_messages/health.json"

repo = EventRepository()
notifier = SlackNotifier(os.environ.get("MONITORING_WEBHOOK_URL"))


# AWS Health
def render_health_message(event: HealthEvent):
    emoji = {"issue": ":warning:", "accountnotification": ":information_source:", "scheduledchange": ":calendar:"}.get(
        event.detail.event_type_category.lower(), ":grey_question:"
    )
    color = {"open": "#FFA500", "closed": "#36A64F", "upcoming": "#439FE0"}.get(
        event.detail.status_code.lower(), "#CCCCCC"
    )
    return render_message(
        HEALTH_TEMPLATE_FILE,
        context={
            "emoji": emoji,
            "color": color,
            "account": event.account,
            "region": event.region,
            "service": event.detail.service,
            "event_type_code": event.detail.event_type_code,
            "event_type_category": event.detail.event_type_category,
            "status": event.detail.status_code,
            "start_time": event.detail.start_time,
            "description": event.detail.event_description,
            "affected_entities": event.detail.affected_entities,
        },
    )


# AWS GuardDuty
def render_guardduty_message(event: GuardDutyFindingEvent):
    if event.detail.severity >= 7:
        severity_label = "HIGH"
        color = "#FF0000"
    elif event.detail.severity >= 4:
        severity_label = "MEDIUM"
        color = "#FFA500"
    else:
        severity_label = "LOW"
        color = "#36A64F"

    return render_message(
        GUARDDUTY_TEMPLATE_FILE,
        context={
            "emoji": ":shield:",
            "color": color,
            "account": event.account,
            "region": event.region,
            "title": event.detail.title,
            "finding_type": event.detail.finding_type,
            "severity_label": severity_label,
            "count": event.detail.count,
            "created_at": event.detail.created_at,
            "description": event.detail.description,
            "instance_id": event.detail.instance_id,
        },
    )


# AWS CloudWatch Alarm
def render_cw_alarm_message(event: CwAlarmEvent):
    state_value = event.detail.state.value
    # Emoji and color
    emoji = {"ALARM": ":red_circle:", "OK": ":recycle:", "INSUFFICIENT_DATA": ":heavy_exclamation_mark:"}.get(
        state_value, ":grey_question:"
    )
    color = {"ALARM": "#FF0000", "OK": "#36A64F", "INSUFFICIENT_DATA": "#FFA500"}.get(state_value, "#CCCCCC")
    metric_info = event.detail.configuration.metrics[0].metric_stat.metric

    return render_message(
        CW_ALARM_TEMPLATE_FILE,
        context={
            "emoji": emoji,
            "color": color,
            "account": event.account,
            "region": event.region,
            "alarm_name": event.detail.alarm_name,
            "alarm_description": event.detail.configuration.description,
            "alarm_reason": event.detail.state.reason,
            "metric_name": metric_info.get("name", "N/A"),
            "metric_namespace": metric_info.get("namespace", "N/A"),
            "metric_dimensions": metric_info.get("dimensions", {}),
            "time": event.time,
        },
    )


# AWS CloudWatch Logs
def render_agent_err_log_message(event):
    pass
