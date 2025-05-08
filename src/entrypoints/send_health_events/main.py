import os

from src.adapters.aws.models import HealthEvent
from src.adapters.notifiers import Message, SlackNotifier
from src.common.utils.objects import extract_items

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")


def create_slack_message(event: HealthEvent) -> Message:
    description = "\n".join(extract_items(event.detail.event_description, "latestDescription"))
    affected_entities = ""
    for item in extract_items(event.detail.affected_entities, "entityValue"):
        affected_entities += f"• `{item}`\n"

    return Message(
        attachments=[
            {
                "mrkdwn_in": ["text"],
                "color": "#Be3125",
                "title": f"Health | AccountID: {event.account}",
                "title_link": "https://health.console.aws.amazon.com/health/home#/dashboard/open-issues",
                "fields": [
                    {"title": "Service", "value": event.detail.service, "short": True},
                    {"title": ":label: EventTypeCode", "value": event.detail.event_type_code, "short": True},
                    {"title": "EventTypeCategory", "value": event.detail.event_type_category, "short": True},
                    {"title": ":clock1: Time", "value": event.detail.start_time, "short": True},
                    {
                        "title": ":memo: Description",
                        "value": description or "No description available",
                        "short": False,
                    },
                    {
                        "title": ":fire: AffectedEntities",
                        "value": affected_entities or "No affected entities",
                        "short": True,
                    },
                ],
            }
        ],
    )


# @logger.inject_lambda_context(log_event=True)
def handler(event: dict, context):
    health_event = HealthEvent.model_validate(event)
    message = create_slack_message(health_event)
    SlackNotifier(webhook_url=WEBHOOK_URL).notify(message)
