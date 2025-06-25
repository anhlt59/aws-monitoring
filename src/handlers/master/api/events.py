from typing import Annotated

from aws_lambda_powertools.event_handler.openapi.params import Body, Query

from src.adapters.api import app, handler
from src.adapters.db.repositories import EventRepository
from src.common.utils.encoding import base64_to_json, json_to_base64
from src.models.event import Status

repo = EventRepository()


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
    decode_cursor = base64_to_json(cursor) if cursor else None
    result = repo.list(start_date, end_date, limit, direction, decode_cursor)
    return {
        "items": result.items,
        "limit": limit,
        "next": json_to_base64(result.cursor) if result.cursor else None,
        "previous": cursor,
    }


@app.put("/events/<event_id>")
def update_event(event_id: str, member: Annotated[str, Body] = None, status: Annotated[Status, Body] = None):
    if member is not None:
        repo.assign_member(event_id, member)
    if status is not None:
        repo.update_status(event_id, status)
    return {"id": event_id}


__all__ = ["handler"]
