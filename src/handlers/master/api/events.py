from typing import Annotated

from aws_lambda_powertools.event_handler.openapi.params import Body, Query
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.adapters.api import app
from src.adapters.db import EventRepository
from src.common.utils.encoding import base64_to_json, json_to_base64
from src.models.monitoring_event import ListEventsDTO, Status, UpdateEventDTO

repo = EventRepository()


# API Routes
@app.get("/events/<event_id>")
def get_event(event_id: str):
    event = repo.get(event_id)
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
        cursor=base64_to_json(cursor) if cursor else None,
    )
    result = repo.list(dto)
    return {
        "items": result.items,
        "limit": limit,
        "next": json_to_base64(result.cursor) if result.cursor else None,
        "previous": cursor,
    }


@app.put("/events/<event_id>")
def update_event(event_id: str, assigned: Annotated[str, Body] = None, status: Annotated[Status, Body] = None):
    dto = UpdateEventDTO(assigned=assigned, status=status)
    repo.update(event_id, dto)
    return {"id": event_id}


@app.delete("/events/<event_id>")
def delete_event(event_id: str):
    repo.delete(event_id)
    return {"id": event_id}


# Entrypoint handler
# @logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
def handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
