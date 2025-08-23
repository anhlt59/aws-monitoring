from src.infras.aws.eventbridge import Event, EventBridgeService


class CWLogEvent(Event):
    source: str = "monitoring.agent.logs"
    detail_type: str = "Error Log Query"


class Publisher:
    def __init__(self, client: EventBridgeService):
        self.client = client

    def publish(self, **event):
        self.client.publish()
