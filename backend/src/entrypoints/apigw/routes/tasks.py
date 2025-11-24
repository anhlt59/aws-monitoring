"""Tasks API Gateway handlers."""

from http import HTTPStatus
from typing import Annotated

from aws_lambda_powertools.event_handler.openapi.params import Query
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel, Field

from src.domain.models.task import TaskPriority, TaskStatus
from src.domain.use_cases.tasks import (
    AddCommentDTO,
    AddCommentToTask,
    CreateTask,
    CreateTaskDTO,
    DeleteTask,
    GetTask,
    ListTasks,
    ListTasksDTO,
    UpdateTask,
    UpdateTaskDTO,
    UpdateTaskStatus,
    UpdateTaskStatusDTO,
)
from src.entrypoints.apigw.base import create_app
from src.entrypoints.apigw.configs import CORS_ALLOW_ORIGIN, CORS_MAX_AGE
from src.entrypoints.apigw.middleware.auth import get_auth_context

# Create app
app = create_app(
    cors_allow_origin=CORS_ALLOW_ORIGIN,
    cors_max_age=CORS_MAX_AGE,
)

# Initialize use cases
create_task_uc = CreateTask()
get_task_uc = GetTask()
list_tasks_uc = ListTasks()
update_task_uc = UpdateTask()
update_task_status_uc = UpdateTaskStatus()
delete_task_uc = DeleteTask()
add_comment_uc = AddCommentToTask()


# Request/Response models
class CreateTaskRequest(BaseModel):
    """Create task request model."""

    title: str = Field(..., min_length=3, max_length=200, description="Task title")
    description: str = Field(..., min_length=10, max_length=5000, description="Task description")
    priority: TaskPriority = Field(..., description="Task priority")
    assigned_user_id: str = Field(..., description="User ID to assign task to")
    event_id: str | None = Field(None, description="Source event ID")
    event_details: dict | None = Field(None, description="Event details snapshot")
    due_date: int | None = Field(None, description="Due date timestamp")


class UpdateTaskRequest(BaseModel):
    """Update task request model."""

    title: str | None = Field(None, min_length=3, max_length=200, description="Task title")
    description: str | None = Field(None, min_length=10, max_length=5000, description="Task description")
    priority: TaskPriority | None = Field(None, description="Task priority")
    assigned_user_id: str | None = Field(None, description="User ID to assign task to")
    due_date: int | None = Field(None, description="Due date timestamp")


class UpdateTaskStatusRequest(BaseModel):
    """Update task status request model."""

    status: TaskStatus = Field(..., description="New task status")


class AddCommentRequest(BaseModel):
    """Add comment request model."""

    comment: str = Field(..., min_length=1, max_length=2000, description="Comment text")


# API Routes
@app.get("/tasks")
def list_tasks(
    status: Annotated[TaskStatus | None, Query] = None,
    priority: Annotated[TaskPriority | None, Query] = None,
    assigned_user_id: Annotated[str | None, Query] = None,
    start_date: Annotated[int | None, Query] = None,
    end_date: Annotated[int | None, Query] = None,
    page: Annotated[int, Query] = 1,
    page_size: Annotated[int, Query] = 20,
):
    """
    List tasks endpoint.

    Supports filtering by status, priority, assigned user, and date range.
    Requires authentication.
    """
    # Get auth context
    get_auth_context(app)

    # Create DTO
    dto = ListTasksDTO(
        status=status,
        priority=priority,
        assigned_user_id=assigned_user_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )

    # Execute use case
    result = list_tasks_uc.execute(dto)

    # Return response
    return {
        "items": [task.model_dump() for task in result.items],
        "total": result.total,
        "page": result.page,
        "page_size": result.page_size,
        "has_more": result.has_more,
    }, HTTPStatus.OK


@app.get("/tasks/<task_id>")
def get_task(task_id: str):
    """
    Get task by ID endpoint.

    Returns task with all comments.
    Requires authentication.
    """
    # Get auth context
    get_auth_context(app)

    # Execute use case
    task = get_task_uc.execute(task_id)

    # Return response
    return task.model_dump(), HTTPStatus.OK


@app.post("/tasks")
def create_task(request: CreateTaskRequest):
    """
    Create task endpoint.

    Requires authentication.
    """
    # Get auth context
    auth = get_auth_context(app)

    # Create DTO
    dto = CreateTaskDTO(
        title=request.title,
        description=request.description,
        priority=request.priority,
        assigned_user_id=request.assigned_user_id,
        event_id=request.event_id,
        event_details=request.event_details,
        due_date=request.due_date,
    )

    # Execute use case
    task = create_task_uc.execute(dto, created_by_user_id=auth.user_id)

    # Return response
    return task.model_dump(), HTTPStatus.CREATED


@app.put("/tasks/<task_id>")
def update_task(task_id: str, request: UpdateTaskRequest):
    """
    Update task endpoint.

    Requires authentication. Users can only update their own tasks unless admin.
    """
    # Get auth context
    auth = get_auth_context(app)

    # Create DTO
    dto = UpdateTaskDTO(
        task_id=task_id,
        title=request.title,
        description=request.description,
        priority=request.priority,
        assigned_user_id=request.assigned_user_id,
        due_date=request.due_date,
    )

    # Execute use case
    task = update_task_uc.execute(dto, requesting_user_id=auth.user_id, is_admin=auth.is_admin())

    # Return response
    return task.model_dump(), HTTPStatus.OK


@app.put("/tasks/<task_id>/status")
def update_task_status(task_id: str, request: UpdateTaskStatusRequest):
    """
    Update task status endpoint.

    Requires authentication.
    """
    # Get auth context
    get_auth_context(app)

    # Create DTO
    dto = UpdateTaskStatusDTO(
        task_id=task_id,
        new_status=request.status,
    )

    # Execute use case
    task = update_task_status_uc.execute(dto)

    # Return response
    return task.model_dump(), HTTPStatus.OK


@app.delete("/tasks/<task_id>")
def delete_task(task_id: str):
    """
    Delete task endpoint.

    Requires admin role.
    """
    # Get auth context
    auth = get_auth_context(app)

    # Check admin permission
    if not auth.is_admin():
        from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

        raise UnauthorizedError("Admin role required to delete tasks")

    # Execute use case
    delete_task_uc.execute(task_id)

    # Return 204 No Content
    return None, HTTPStatus.NO_CONTENT


@app.post("/tasks/<task_id>/comments")
def add_comment(task_id: str, request: AddCommentRequest):
    """
    Add comment to task endpoint.

    Requires authentication.
    """
    # Get auth context
    auth = get_auth_context(app)

    # Create DTO
    dto = AddCommentDTO(
        task_id=task_id,
        comment_text=request.comment,
    )

    # Execute use case
    task = add_comment_uc.execute(dto, user_id=auth.user_id)

    # Return response
    return task.model_dump(), HTTPStatus.CREATED


# Lambda handler
def handler(event: dict, context: LambdaContext) -> dict:
    """Lambda function handler for tasks endpoints."""
    return app.resolve(event, context)
