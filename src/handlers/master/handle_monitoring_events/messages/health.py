from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent

from src.adapters.notifiers import Message


def create_health_message(event: EventBridgeEvent):
    detail = event.detail
    status = detail.get("statusCode", "").upper()
    description = detail.get("eventDescription", [{}])[0].get("latestDescription", "No description provided.")

    # Format affected entities
    if affected_entities := detail.get("affectedEntities", []):
        entities_text = "\n".join(f"• `{e['entityValue']}` — *{e['status'].capitalize()}*" for e in affected_entities)
    else:
        entities_text = "No affected entities listed."

    # Choose emoji and color based on category or status
    emoji = {"issue": ":warning:", "accountnotification": ":information_source:", "scheduledchange": ":calendar:"}.get(
        detail.get("eventTypeCategory", "").lower(), ":grey_question:"
    )
    color = {"open": "#FFA500", "closed": "#36A64F", "upcoming": "#439FE0"}.get(status.lower(), "#CCCCCC")

    return Message(
        attachments=[
            {
                "color": color,
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"{emoji} Health Event: {detail.get('eventTypeCode')}",
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
                            {"type": "mrkdwn", "text": f"* :gear: Service:*\n{detail.get('service')}"},
                            {
                                "type": "mrkdwn",
                                "text": f"* :label: Category:*\n{detail.get('eventTypeCategory', '').capitalize()}",
                            },
                            {"type": "mrkdwn", "text": f"* :beginner: Status:*\n{status}"},
                            {"type": "mrkdwn", "text": f"* :calendar: Start Time:*\n{detail.get('startTime', 'N/A')}"},
                        ],
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"*Description:*\n{description}"},
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"*Affected Entities:*\n{entities_text}"},
                    },
                ],
            }
        ]
    )
