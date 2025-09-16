from typing import Annotated

from aws_lambda_powertools.event_handler.openapi.params import Query
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.common.utils.encoding import json_to_base64
from src.entrypoints.apigw.base import create_app
from src.entrypoints.apigw.configs import CORS_ALLOW_ORIGIN, CORS_MAX_AGE
from src.infra.db.repositories import EventRepository
from src.modules.master.models.event import ListEventsDTO

app = create_app(
    cors_allow_origin=CORS_ALLOW_ORIGIN,
    cors_max_age=CORS_MAX_AGE,
)
event_repo = EventRepository()


# API Routes
@app.get("/events/<event_id>")
def get_event(event_id: str):
    event = event_repo.get(event_id)
    return event.model_dump()


@app.get("/events")
def list_events(
    start_date: Annotated[int, Query] = None,
    end_date: Annotated[int, Query] = None,
    limit: Annotated[int, Query] = 50,
    direction: Annotated[str, Query] = "desc",
    cursor: Annotated[str, Query] = None,
):
    dto = ListEventsDTO(
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        direction=direction,
        cursor=cursor,
    )
    result = event_repo.list(dto)
    return {
        "items": result.items,
        "limit": limit,
        "next": json_to_base64(result.cursor) if result.cursor else None,
        "previous": cursor,
    }


# Entrypoint handler
# @logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
def handler(event: dict, context: LambdaContext) -> dict:
    print(dict(event))
    return app.resolve(event, context)
