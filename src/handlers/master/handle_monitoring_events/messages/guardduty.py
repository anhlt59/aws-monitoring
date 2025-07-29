from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent

from src.adapters.notifiers import Message


def create_guardduty_message(event: EventBridgeEvent):
    detail = event.detail
    instance_id = detail.get("resource", {}).get("instanceDetails", {}).get("instanceId", "N/A")
    title = detail.get("title", "GuardDuty Finding")
    description = detail.get("description", "No description provided.")
    finding_type = detail.get("type", "Unknown")
    severity = detail.get("severity", 0)
    count = detail.get("service", {}).get("count", 1)
    created_at = detail.get("createdAt", "N/A")

    # Severity label + emoji
    if severity >= 7:
        severity_label = "HIGH"
        color = "#FF0000"
    elif severity >= 4:
        severity_label = "MEDIUM"
        color = "#FFA500"
    else:
        severity_label = "LOW"
        color = "#36A64F"

    return Message(
        attachments=[
            {
                "color": color,
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f":shield: GuardDuty: {title}",
                            "emoji": True,
                        },
                    },
                    {
                        "type": "context",
                        "elements": [{"type": "mrkdwn", "text": f"*Account: {event.account}  |  {event.region}*"}],
                    },
                    {"type": "divider"},
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f":label:*Type:*\n{finding_type}"},
                            {"type": "mrkdwn", "text": f":beginner:*Severity:*\n{severity_label}"},
                            {"type": "mrkdwn", "text": f":chart_with_upwards_trend:*Count:*\n{count}"},
                            {"type": "mrkdwn", "text": f":alarm_clock:*Time:*\n{created_at}"},
                        ],
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"*Description:*\n{description}"},
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"*Resource ID:*\n• `{instance_id}`"},
                    },
                ],
            }
        ]
    )
