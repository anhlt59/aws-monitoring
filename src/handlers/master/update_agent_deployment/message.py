from src.adapters.aws.cloudformation import CfnStackEvent, CfnStackStatus
from src.adapters.notifiers import Message


def create_cfn_message(event: CfnStackEvent) -> Message:
    match event.stack_status:
        case CfnStackStatus.CREATE_COMPLETE | CfnStackStatus.UPDATE_COMPLETE:
            emoji = ":white_check_mark:"
            color = "#36A64F"
        case CfnStackStatus.CREATE_FAILED | CfnStackStatus.UPDATE_FAILED | CfnStackStatus.UPDATE_ROLLBACK_FAILED:
            emoji = ":x:"
            color = "#FF0000"
        case _:
            emoji = ":warning:"
            color = "#FFA500"

    console_link = (
        f"https://console.aws.amazon.com/cloudformation/home?region={event.region}#/stacks/stackinfo?"
        f"filteringStatus=active&filteringText={event.stack_name}&viewNested=true&stackId={event.stack_id}"
    )

    return Message(
        attachments=[
            {
                "color": color,
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"{emoji} CloudFormation: {event.stack_name}",
                            "emoji": True,
                        },
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Account:* `{event.account}`   |   *Region:* `{event.region}`",
                            }
                        ],
                    },
                    {"type": "divider"},
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*Status:*\n`{event.stack_status}`"},
                            {"type": "mrkdwn", "text": f"*Time:*\n{event.time}"},
                        ],
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"*Reason:*\n{event.stack_status_reason}"},
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"<{console_link}|:link: View in AWS Console>",
                        },
                    },
                ],
            }
        ]
    )
