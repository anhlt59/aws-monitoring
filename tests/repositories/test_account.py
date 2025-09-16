import time

import pytest

from src.common.constants import AWS_REGION
from src.common.exceptions import NotFoundError
from src.infra.aws.data_classes import CfnStackStatus
from src.modules.master.models.agent import Agent, UpdateAgentDTO


def test_create_agent(agent_repo):
    agent = Agent(
        id="000000000000",
        region=AWS_REGION,
        status=CfnStackStatus.CREATE_COMPLETE,
        deployed_at=int(time.time()),
    )
    agent_repo.create(agent)
    retrieved_agent = agent_repo.get(agent.id)
    assert retrieved_agent.id == agent.id


def test_update_agent(agent_repo, dummy_agent):
    agent_repo.get(dummy_agent.id)

    update_dto = UpdateAgentDTO(status=CfnStackStatus.UPDATE_COMPLETE, region="ap-northeast-1")
    agent_repo.update(dummy_agent.id, update_dto)

    updated_agent = agent_repo.get(dummy_agent.id)
    assert updated_agent.status == update_dto.status
    assert updated_agent.region == update_dto.region


def test_delete_agent(agent_repo, dummy_agent):
    agent_repo.delete(dummy_agent.id)
    with pytest.raises(NotFoundError):
        agent_repo.get(dummy_agent.id)


def test_list_agents(agent_repo, dummy_agent):
    agents = agent_repo.list()
    assert len(agents.items) > 0
    assert any(acc.id == dummy_agent.id for acc in agents.items)
