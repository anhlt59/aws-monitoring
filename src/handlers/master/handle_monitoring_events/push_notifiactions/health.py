from src.adapters.aws.health import EventTypeDef
from src.adapters.notifiers import Message, SlackNotifier
from src.common.logger import logger
from src.common.utils.objects import extract_items


def create_slack_message(event: EventTypeDef) -> Message:
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


def push_health_notification(event: dict, notifier: SlackNotifier):
    # health_event = HealthEvent.model_validate(event)
    message = create_slack_message(event)
    notifier.notify(message)
    logger.info("Sent health event")
