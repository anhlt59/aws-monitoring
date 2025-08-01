import json
import time
from uuid import uuid4

from src.handlers.api.agents.main import handler
from src.models import Agent
from tests.mock import mock_api_gateway_event, mock_lambda_context


def test_list_agents(agent_repo):
    now = int(time.time())
    for i in range(3):
        agent_repo.create(
            Agent(
                id=f"{now}-{uuid4()}",
                region="us-east-1",
                deployed_at=now - i * 60,
            )
        )

    context = mock_lambda_context("list_agents")

    event = mock_api_gateway_event(
        method="GET",
        path="/agents",
    )
    response = handler(event, context)
    data = json.loads(response["body"])
    assert len(data["items"]) == 3, "Expected 3 agents in the response"


def test_get_agent(agent_repo, dummy_agent):
    event = mock_api_gateway_event(
        method="GET",
        path=f"/agents/{dummy_agent.id}",
    )
    context = mock_lambda_context("get_agent")
    response = handler(event, context)
    data = json.loads(response["body"])

    assert data["id"] == dummy_agent.id, "Expected agent ID to match"
