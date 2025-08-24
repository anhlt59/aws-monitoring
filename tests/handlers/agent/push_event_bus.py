import json

import boto3

boto3.setup_default_session(profile_name="lc-stg")


def handle_monitoring_events():
    from src.infras.aws import EventBridgeService
    from tests.conftest import TEST_DIR

    service = EventBridgeService("monitoring-master-cm-MonitoringEventBus")
    with open(TEST_DIR / "data" / "logs_event.json") as f:
        data = json.load(f)

    service.put_events(
        {
            "Time": data["time"],
            "Resources": data["resources"],
            "DetailType": data["detail-type"],
            "EventBusName": "monitoring-master-cm-MonitoringEventBus",
            "Source": data["source"],
            "Detail": json.dumps(data["detail"]),
        }
    )


if __name__ == "__main__":
    handle_monitoring_events()
