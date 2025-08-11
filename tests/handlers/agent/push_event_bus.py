import json


def handle_monitoring_events():
    import boto3

    boto3.setup_default_session(profile_name="lc-stg")

    from src.adapters.aws.eventbridge import Event, EventBridgeService
    from tests.conftest import TEST_DIR

    service = EventBridgeService()
    with open(TEST_DIR / "data" / "logs_event.json") as f:
        data = json.load(f)

    service.publish(
        Event(
            source=data["source"],
            detail_type=data["detail_type"],
            detail=data["detail"],
        )
    )


if __name__ == "__main__":
    handle_monitoring_events()
