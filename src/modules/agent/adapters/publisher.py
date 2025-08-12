from src.infras.aws.eventbridge import Event, EventBridgeService


class MonitoringEvent(Event):
    source: str = "monitoring.agent.logs"
    detail_type: str = "Error Log Query"


class MonitoringPublisher:
    def __init__(self, client: EventBridgeService):
        self.client = client

    def publish(self, **event: MonitoringEvent):
        self.client.publish()
