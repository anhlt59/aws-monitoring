from aws_lambda_powertools.utilities.typing import LambdaContext

from src.modules.master.handlers.api.configs import CORS_ALLOW_ORIGIN, CORS_MAX_AGE
from src.modules.master.services.api import create_app
from src.modules.master.services.repositories import AgentRepository

app = create_app(
    cors_allow_origin=CORS_ALLOW_ORIGIN,
    cors_max_age=CORS_MAX_AGE,
)
agent_repo = AgentRepository()


# API Routes
@app.get("/agents/<agent_id>")
def get_agent(agent_id: str):
    agent = agent_repo.get(agent_id)
    return agent.model_dump()


@app.get("/agents")
def list_agents():
    result = agent_repo.list()
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
