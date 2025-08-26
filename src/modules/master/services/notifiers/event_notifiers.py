from src.infras.aws.data_classes import (
    CfnStackEvent,
    CfnStackStatus,
    CwAlarmEvent,
    CwLogEvent,
    EventBridgeEvent,
    GuardDutyFindingEvent,
    HealthEvent,
)
from src.modules.master.configs import (
    CFN_TEMPLATE_FILE,
    CW_ALARM_TEMPLATE_FILE,
    CW_LOG_TEMPLATE_FILE,
    GUARDDUTY_TEMPLATE_FILE,
    HEALTH_TEMPLATE_FILE,
    METADATA,
)

from .base import Message, SlackClient, render_message


class EventNotifier:
    def __init__(self, client: SlackClient):
        self.client = client

    @staticmethod
    def event_to_message(event: EventBridgeEvent) -> Message:
        raise NotImplementedError("Subclasses must implement event_to_message method")

    def notify(self, event: EventBridgeEvent):
        message = self.event_to_message(event)
        self.client.send(message)


class CWAlarmNotifier(EventNotifier):
    @staticmethod
    def event_to_message(event: EventBridgeEvent) -> Message:
        event = CwAlarmEvent(event)
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
                "account": {"id": event.account, "name": METADATA.get(event.account), "region": event.region},
                "alarm_name": event.detail.alarm_name,
                "alarm_description": event.detail.configuration.description,
                "alarm_reason": event.detail.state.reason,
                "metric_name": metric_info.get("name", "N/A"),
                "metric_namespace": metric_info.get("namespace", "N/A"),
                "metric_dimensions": metric_info.get("dimensions", {}),
                "time": event.time,
            },
        )


class CWLogNotifier(EventNotifier):
    @staticmethod
    def event_to_message(event: EventBridgeEvent) -> Message:
        event = CwLogEvent(event)
        return render_message(
            CW_LOG_TEMPLATE_FILE,
            context={
                "emoji": ":warning:",
                "color": "#FF0000",
                "account": {"id": event.account, "name": METADATA.get(event.account), "region": event.region},
                "detail_type": event.detail_type,
                "log_group_name": event.detail.log_group_name,
                "logs": event.detail.logs,
                "time": event.time,
            },
        )


class GuardDutyNotifier(EventNotifier):
    @staticmethod
    def event_to_message(event: EventBridgeEvent) -> Message:
        event = GuardDutyFindingEvent(event)
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
                "account": {"id": event.account, "name": METADATA.get(event.account), "region": event.region},
                "title": event.detail.title,
                "finding_type": event.detail.finding_type,
                "severity_label": severity_label,
                "count": event.detail.count,
                "created_at": event.detail.created_at,
                "description": event.detail.description,
                "instance_id": event.detail.instance_id,
            },
        )


class HealthNotifier(EventNotifier):
    @staticmethod
    def event_to_message(event: EventBridgeEvent) -> Message:
        event = HealthEvent(event)
        emoji = {
            "issue": ":warning:",
            "accountnotification": ":information_source:",
            "scheduledchange": ":calendar:",
        }.get(event.detail.event_type_category.lower(), ":grey_question:")
        color = {"open": "#FFA500", "closed": "#36A64F", "upcoming": "#439FE0"}.get(
            event.detail.status_code.lower(), "#CCCCCC"
        )
        return render_message(
            HEALTH_TEMPLATE_FILE,
            context={
                "emoji": emoji,
                "color": color,
                "account": {"id": event.account, "name": METADATA.get(event.account), "region": event.region},
                "service": event.detail.service,
                "event_type_code": event.detail.event_type_code,
                "event_type_category": event.detail.event_type_category,
                "status": event.detail.status_code,
                "start_time": event.detail.start_time,
                "description": event.detail.event_description,
                "affected_entities": event.detail.affected_entities,
            },
        )


class CloudFormationNotifier(EventNotifier):
    @staticmethod
    def event_to_message(event: EventBridgeEvent) -> Message:
        event = CfnStackEvent(event)
        match event.stack_data.status:
            case CfnStackStatus.CREATE_COMPLETE | CfnStackStatus.UPDATE_COMPLETE:
                emoji = ":rocket:"
                color = "#36A64F"
            case CfnStackStatus.CREATE_FAILED | CfnStackStatus.UPDATE_FAILED | CfnStackStatus.UPDATE_ROLLBACK_FAILED:
                emoji = ":x:"
                color = "#FF0000"
            case _:
                emoji = ":warning:"
                color = "#FFA500"

        return render_message(
            CFN_TEMPLATE_FILE,
            context={
                "color": color,
                "emoji": emoji,
                "account": {"id": event.account, "name": METADATA.get(event.account), "region": event.region},
                "stack_name": event.stack_data.name,
                "stack_status": event.stack_data.status,
                "stack_status_reason": event.stack_data.status_reason,
                "time": event.time,
                "console_link": (
                    f"https://console.aws.amazon.com/cloudformation/home?region={event.region}#/stacks/stackinfo?filtering"
                    f"Status=active&filteringText={event.stack_data.name}&viewNested=true&stackId={event.stack_data.id}"
                ),
            },
        )
