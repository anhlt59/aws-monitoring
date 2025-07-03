import json


def handle_monitoring_events():
    import boto3

    boto3.setup_default_session(profile_name="neos")

    from src.adapters.aws.eventbridge import EventBridgeService, EventsRequestEntry
    from tests.conftest import TEST_DIR
    from tests.mock import load_events

    service = EventBridgeService()
    for event in load_events(file_path=TEST_DIR / "events" / "health_event.json"):
        service.publish_events(
            [
                EventsRequestEntry(
                    Source="monitoring.agent.health",
                    DetailType=event.detail_type,
                    Detail=json.dumps(event.raw_event),
                )
            ]
        )


if __name__ == "__main__":
    handle_monitoring_events()
