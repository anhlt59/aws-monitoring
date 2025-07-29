import re
from enum import Enum

from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent


class CfnStackStatus(str, Enum):
    CREATE_COMPLETE = "CREATE_COMPLETE"
    UPDATE_COMPLETE = "UPDATE_COMPLETE"
    DELETE_COMPLETE = "DELETE_COMPLETE"
    UPDATE_ROLLBACK_COMPLETE = "UPDATE_ROLLBACK_COMPLETE"
    CREATE_FAILED = "CREATE_FAILED"
    UPDATE_FAILED = "UPDATE_FAILED"
    DELETE_FAILED = "DELETE_FAILED"
    UPDATE_ROLLBACK_FAILED = "UPDATE_ROLLBACK_FAILED"


class CfnStackEvent(EventBridgeEvent):
    arn_compiler = re.compile(r"^arn:aws:cloudformation.*stack/(?P<name>[^/]+)/(?P<id>[^/]+)$")

    @property
    def stack_id(self) -> str:
        return self["detail"]["stack-id"]

    @property
    def stack_name(self) -> str:
        groups = self.arn_compiler.search(self["detail"]["stack-id"])
        return groups.group("name")

    @property
    def stack_status(self) -> str:
        return self["detail"].get("status-details", {}).get("status", "")

    @property
    def stack_status_reason(self) -> str:
        return self["detail"].get("status-details", {}).get("status-reason", "")
