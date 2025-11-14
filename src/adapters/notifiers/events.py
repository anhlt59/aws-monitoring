from src.adapters.aws.data_classes import (
    CfnStackEvent,
    CfnStackStatus,
    CwAlarmEvent,
    CwLogEvent,
    EventBridgeEvent,
    GuardDutyFindingEvent,
    HealthEvent,
)
from src.common.constants import (
    CFN_TEMPLATE_FILE,
    CW_ALARM_TEMPLATE_FILE,
    CW_LOG_TEMPLATE_FILE,
    GUARDDUTY_TEMPLATE_FILE,
    HEALTH_TEMPLATE_FILE,
    METADATA,
)
from src.common.enums import (
    AlarmState,
    CfnStackStatusType,
    EventSource,
    HealthEventCategory,
    HealthEventStatus,
    SeverityLevel,
)

from .base import Message, SlackClient, render_message


def cw_alarm_event_to_message(event: EventBridgeEvent) -> Message:
    event = CwAlarmEvent(event)
    state_value = event.detail.state.value
    # Get alarm state enum (fallback to ALARM if unknown)
    try:
        alarm_state = AlarmState(state_value)
    except ValueError:
        alarm_state = AlarmState.ALARM

    emoji = alarm_state.emoji()
    color = alarm_state.color()
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


def cw_log_event_to_message(event: EventBridgeEvent) -> Message:
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


def guardduty_event_to_message(event: EventBridgeEvent) -> Message:
    event = GuardDutyFindingEvent(event)
    severity = SeverityLevel.from_score(event.detail.severity)

    return render_message(
        GUARDDUTY_TEMPLATE_FILE,
        context={
            "emoji": ":shield:",
            "color": severity.color(),
            "account": {"id": event.account, "name": METADATA.get(event.account), "region": event.region},
            "title": event.detail.title,
            "finding_type": event.detail.finding_type,
            "severity_label": severity.value,
            "count": event.detail.count,
            "created_at": event.detail.created_at,
            "description": event.detail.description,
            "instance_id": event.detail.instance_id,
        },
    )


def health_event_to_message(event: EventBridgeEvent) -> Message:
    event = HealthEvent(event)
    # Get health event category enum (fallback to ISSUE if unknown)
    try:
        category = HealthEventCategory(event.detail.event_type_category.lower())
    except ValueError:
        category = HealthEventCategory.ISSUE

    # Get health event status enum (fallback to OPEN if unknown)
    try:
        status = HealthEventStatus(event.detail.status_code.lower())
    except ValueError:
        status = HealthEventStatus.OPEN

    emoji = category.emoji()
    color = status.color()
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


def cfn_event_to_message(event: EventBridgeEvent) -> Message:
    event = CfnStackEvent(event)

    # Determine status type based on CloudFormation stack status
    match event.stack_data.status:
        case CfnStackStatus.CREATE_COMPLETE | CfnStackStatus.UPDATE_COMPLETE:
            status_type = CfnStackStatusType.SUCCESS
        case CfnStackStatus.CREATE_FAILED | CfnStackStatus.UPDATE_FAILED | CfnStackStatus.UPDATE_ROLLBACK_FAILED:
            status_type = CfnStackStatusType.FAILURE
        case _:
            status_type = CfnStackStatusType.WARNING

    emoji = status_type.emoji()
    color = status_type.color()

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


class EventNotifier:
    def __init__(self, client: SlackClient):
        self.client = client

    @staticmethod
    def event_to_message(event: EventBridgeEvent) -> Message:
        match event.source:
            case EventSource.AWS_HEALTH.value | EventSource.AGENT_HEALTH.value:
                return health_event_to_message(event)
            case EventSource.AWS_GUARDDUTY.value | EventSource.AGENT_GUARDDUTY.value:
                return guardduty_event_to_message(event)
            case EventSource.AWS_CLOUDWATCH.value | EventSource.AGENT_CLOUDWATCH.value:
                return cw_alarm_event_to_message(event)
            case EventSource.AGENT_LOGS.value:
                return cw_log_event_to_message(event)
            case EventSource.AWS_CLOUDFORMATION.value | EventSource.AGENT_CLOUDFORMATION.value:
                return cfn_event_to_message(event)
            case _:
                raise ValueError(f"Unknown event source: {event.source}")

    async def notify(self, event: EventBridgeEvent):
        message = self.event_to_message(event)
        await self.client.send(message)
