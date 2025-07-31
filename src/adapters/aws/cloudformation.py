import re
from enum import Enum

from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent
from aws_lambda_powertools.utilities.data_classes.common import DictWrapper


class CfnStackStatus(str, Enum):
    CREATE_COMPLETE = "CREATE_COMPLETE"
    UPDATE_COMPLETE = "UPDATE_COMPLETE"
    DELETE_COMPLETE = "DELETE_COMPLETE"
    UPDATE_ROLLBACK_COMPLETE = "UPDATE_ROLLBACK_COMPLETE"
    CREATE_FAILED = "CREATE_FAILED"
    UPDATE_FAILED = "UPDATE_FAILED"
    DELETE_FAILED = "DELETE_FAILED"
    UPDATE_ROLLBACK_FAILED = "UPDATE_ROLLBACK_FAILED"


# EventBridge Event --------------------------
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
