from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent
from aws_lambda_powertools.utilities.data_classes.common import DictWrapper


# EventBridge Event --------------------------
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
