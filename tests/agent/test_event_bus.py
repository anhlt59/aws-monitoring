import json

import boto3
from types_boto3_events.type_defs import PutEventsRequestEntryTypeDef

from tests.conftest import TEST_DIR
from tests.mock import load_events

client = boto3.client("events", region_name="us-east-1", endpoint_url="http://localhost:4566")


def test_handle_monitoring_events():
    # truncate_event_table()
    for event in load_events(file_path=TEST_DIR / "events" / "health_event.json"):
        client.put_events(
            Entries=[
                PutEventsRequestEntryTypeDef(
                    Source=event.source,
                    DetailType=event.detail_type,
                    Detail=json.dumps(event.raw_event),
                    EventBusName="default",
                )
            ]
        )
