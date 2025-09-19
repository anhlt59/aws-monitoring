import json
import time
from uuid import uuid4

from src.domain.models import Event
from src.entrypoints.apigw.events.main import handler
from tests.mock import mock_api_gateway_event, mock_lambda_context


def test_list_events(event_repo):
    now = int(time.time())
    for i in range(11):
        event_repo.create(
            Event(
                id=f"{now}-{uuid4()}",
                account="000000000000",
                region="us-east-1",
                source="agent.test",
                detail={"message": f"Test event {i}"},
                detail_type="TestEvent",
                resources=[],
                published_at=now - i * 60,
                updated_at=now - i * 60,
            )
        )

    context = mock_lambda_context("list_events")

    # without params
    event = mock_api_gateway_event(
        method="GET",
        path="/events",
        params={"limit": 10},
    )
    response = handler(event, context)
    data = json.loads(response["body"])
    assert len(data["items"]) == 10, "Expected 10 events in the response"
    assert data["next"] is not None, "Expected a next cursor in the response"
    # get the next page
    event = mock_api_gateway_event(
        method="GET",
        path="/events",
        params={"limit": 10, "cursor": data["next"]},
    )
    response = handler(event, context)
    data = json.loads(response["body"])
    assert len(data["items"]) == 1

    # Invalid limit param
    event = mock_api_gateway_event(
        method="GET",
        path="/events",
        params={"limit": 1},
    )
    response = handler(event, context)
    data = json.loads(response["body"])
    assert response["statusCode"] == 400, "Expected 400 Bad Request for invalid params"
    assert len(data["errors"]) == 1, "Expected one error in the response"

    # Filtered by start_date & end_date
    # TODO: Fix this test
    # event = mock_api_gateway_event(
    #     method="GET",
    #     path="/events",
    #     params={"start_date": now - 60},
    # )
    # response = handler(event, context)
    # data = json.loads(response["body"])
    # assert len(data["items"]) == 1, "Expected one event in the response"

    event = mock_api_gateway_event(
        method="GET",
        path="/events",
        params={"start_date": now - 600, "end_date": now},
    )
    response = handler(event, context)
    data = json.loads(response["body"])
    assert len(data["items"]) == 10, "Expected 10 events in the response"


def test_get_event(event_repo, dummy_event):
    event = mock_api_gateway_event(
        method="GET",
        path=f"/events/{dummy_event.persistence_id}",
    )
    context = mock_lambda_context("get_event")
    response = handler(event, context)
    data = json.loads(response["body"])

    assert data["id"] == dummy_event.id, f"Expected event ID {dummy_event.id}"
