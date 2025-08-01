from aws_lambda_powertools.utilities.typing import LambdaContext

from src.adapters.api import app
from src.adapters.db import AgentRepository

repo = AgentRepository()


# API Routes
@app.get("/agent/<agent_id>")
def get_agent(agent_id: str):
    agent = repo.get(agent_id)
    return agent.model_dump()


@app.get("/agents")
def list_agents():
    result = repo.list()
    return {
        "items": result.items,
        "limit": result.limit,
        "next": None,
        "previous": None,
    }


# Entrypoint handler
# @logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
def handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
