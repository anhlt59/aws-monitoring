from http import HTTPStatus
from typing import Annotated

from aws_lambda_powertools.event_handler.openapi.params import Query
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel, Field

from src.adapters.db.repositories import EventRepository
from src.common.utils.encoding import json_to_base64
from src.domain.models.event import ListEventsDTO
from src.domain.models.task import TaskPriority
from src.domain.use_cases.tasks import CreateTaskFromEvent, CreateTaskFromEventDTO
from src.entrypoints.apigw.base import create_app
from src.entrypoints.apigw.configs import CORS_ALLOW_ORIGIN, CORS_MAX_AGE
from src.entrypoints.apigw.middleware.auth import get_auth_context

app = create_app(
    cors_allow_origin=CORS_ALLOW_ORIGIN,
    cors_max_age=CORS_MAX_AGE,
)
event_repo = EventRepository()
create_task_from_event_uc = CreateTaskFromEvent()


# Request models
class CreateTaskFromEventRequest(BaseModel):
    """Request model for creating task from event."""

    assigned_user_id: str = Field(..., description="User ID to assign task to")
    title: str | None = Field(None, description="Custom task title")
    description: str | None = Field(None, description="Custom task description")
    priority: TaskPriority | None = Field(None, description="Task priority")
    due_date: int | None = Field(None, description="Due date timestamp")


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


@app.post("/events/<event_id>/create-task")
def create_task_from_event(event_id: str, request: CreateTaskFromEventRequest):
    """
    Create a task from an event.

    Requires authentication. Creates a task linked to the specified event.
    """
    # Get auth context
    auth = get_auth_context(app)

    # Create task from event
    dto = CreateTaskFromEventDTO(
        event_id=event_id,
        assigned_user_id=request.assigned_user_id,
        title=request.title,
        description=request.description,
        priority=request.priority,
        due_date=request.due_date,
    )

    task = create_task_from_event_uc.execute(dto, created_by_user_id=auth.user_id)

    return task.model_dump(), HTTPStatus.CREATED


# Entrypoint handler
# @logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
def handler(event: dict, context: LambdaContext) -> dict:
    print(dict(event))
    return app.resolve(event, context)
