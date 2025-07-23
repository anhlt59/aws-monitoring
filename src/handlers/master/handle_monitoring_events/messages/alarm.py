from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent

from src.adapters.notifiers import Message


def create_alarm_message(event: EventBridgeEvent):
    detail = event.detail
    description = detail.get("configuration", {}).get("description", "")
    state_value = detail["state"]["value"]
    metric_info = detail["configuration"]["metrics"][0]["metricStat"]["metric"]

    # Convert dimensions to Slack-friendly text
    dim_text = "\n".join([f"• *{k}*: `{v}`" for k, v in metric_info.get("dimensions", {}).items()]) or ">N/A"

    # Emoji and color
    state_emoji = {"ALARM": ":red_circle:", "OK": ":green_circle:", "INSUFFICIENT_DATA": ":orange_circle:"}.get(
        state_value, ":grey_question:"
    )
    color = {"ALARM": "#FF0000", "OK": "#36A64F", "INSUFFICIENT_DATA": "#FFA500"}.get(state_value, "#CCCCCC")

    return Message(
        attachments=[
            {
                "color": color,
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"{state_emoji} CloudWatch Alarm: {detail.get('alarmName')}",
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
                            {
                                "type": "mrkdwn",
                                "text": f"* :bar_chart: Metric:*\n{metric_info['namespace']}/{metric_info['name']}",
                            },
                            {"type": "mrkdwn", "text": f"* :alarm_clock: Time:*\n{event.time}"},
                        ],
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"* Description:*\n{description or 'No description'}"},
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"* Reason:*\n{detail['state']['reason']}"},
                    },
                    {"type": "section", "text": {"type": "mrkdwn", "text": f"* Dimensions:*\n{dim_text}"}},
                ],
            }
        ]
    )
