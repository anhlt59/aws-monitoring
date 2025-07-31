from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent
from aws_lambda_powertools.utilities.data_classes.common import DictWrapper


# EventBridge Event --------------------------
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
