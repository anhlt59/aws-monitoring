import re
from enum import Enum
from aws_lambda_powertools.utilities.data_classes import (
    CloudWatchAlarmData,
    EventBridgeEvent,
    event_source
)

from aws_lambda_powertools.utilities.data_classes.common import DictWrapper

__all__ = [
    "event_source",
    "CfnStackEvent",
    "CfnStackStatus",
    "CwAlarmEvent",
    "EventBridgeEvent",
    "HealthEvent",
    "GuardDutyFindingEvent",
]


# Health Event --------------------------
class HealthData(DictWrapper):
    @property
    def event_arn(self) -> str:
        return self["eventArn"]

    @property
    def event_description(self) -> str:
        return self.get("eventDescription", [{}])[0].get("latestDescription", "No description provided.")

    @property
    def event_type_code(self) -> str:
        return self["eventTypeCode"]

    @property
    def event_type_category(self) -> str:
        return self["eventTypeCategory"].capitalize()

    @property
    def service(self) -> str:
        return self["service"]

    @property
    def status_code(self) -> str:
        return self["statusCode"].upper()

    @property
    def affected_entities(self) -> list:
        return self.get("affectedEntities")

    @property
    def start_time(self) -> str:
        return self["startTime"]


class HealthEvent(EventBridgeEvent):
    @property
    def detail(self) -> HealthData:
        return HealthData(self["detail"])


# GuardDuty Finding Event --------------------------
class FindingData(DictWrapper):
    @property
    def title(self):
        return self.get("title", "GuardDuty Finding")

    @property
    def description(self):
        return self.get("description", "No description provided.")

    @property
    def finding_type(self) -> str:
        return self.get("type", "Unknown")

    @property
    def severity(self) -> int:
        return self.get("severity", 0)

    @property
    def count(self) -> int:
        return self.get("service", {}).get("count", 1)

    @property
    def created_at(self) -> str:
        return self.get("createdAt", "N/A")

    @property
    def instance_id(self) -> str:
        return self.get("resource", {}).get("instanceDetails", {}).get("instanceId", "N/A")


class GuardDutyFindingEvent(EventBridgeEvent):
    @property
    def detail(self) -> FindingData:
        return FindingData(self["detail"])


# CloudWatch Alarm Event --------------------------
class CwAlarmEvent(EventBridgeEvent):
    @property
    def detail(self) -> CloudWatchAlarmData:
        return CloudWatchAlarmData(self["detail"])


# CloudFormation Stack Event --------------------------
class CfnStackStatus(str, Enum):
    CREATE_COMPLETE = "CREATE_COMPLETE"
    UPDATE_COMPLETE = "UPDATE_COMPLETE"
    DELETE_COMPLETE = "DELETE_COMPLETE"
    UPDATE_ROLLBACK_COMPLETE = "UPDATE_ROLLBACK_COMPLETE"
    CREATE_FAILED = "CREATE_FAILED"
    UPDATE_FAILED = "UPDATE_FAILED"
    DELETE_FAILED = "DELETE_FAILED"
    UPDATE_ROLLBACK_FAILED = "UPDATE_ROLLBACK_FAILED"


class CfnStackData(DictWrapper):
    arn_compiler = re.compile(r"^arn:aws:cloudformation.*stack/(?P<name>[^/]+)/(?P<id>[^/]+)$")

    @property
    def id(self) -> str:
        return self["stack-id"]

    @property
    def name(self) -> str:
        try:
            groups = self.arn_compiler.search(self["stack-id"])
            return groups.group("name")
        except Exception:
            return "Unknown"

    @property
    def status(self) -> str:
        return self["status-details"]["status"]

    @property
    def status_reason(self) -> str:
        return self["status-details"]["status-reason"]


class CfnStackEvent(EventBridgeEvent):
    @property
    def stack_data(self) -> CfnStackData:
        return CfnStackData(self["detail"])
