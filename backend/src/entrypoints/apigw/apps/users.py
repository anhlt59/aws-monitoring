"""Users API Gateway handlers."""

from http import HTTPStatus
from typing import Annotated

from aws_lambda_powertools.event_handler.openapi.params import Query
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel, Field

from domain.iam.exceptions import AdminRequiredError, CrossUserAccessError
from entrypoints.apigw.base import admin_required
from src.adapters.db.repositories import UserRepository
from src.domain.iam.models import UserProfile, UserRole
from src.domain.iam.use_cases.user import ChangePasswordDTO, CreateUserDTO, ListUsersDTO, UpdateUserDTO, UserUseCases
from src.entrypoints.apigw.base import create_app, login_required

# ------------------------------
# Initialization
# ------------------------------
use_cases = UserUseCases(
    user_repository=UserRepository(),
)
app = create_app()


# ------------------------------
# Request/Response models
# ------------------------------
class CreateUserRequest(BaseModel):
    email: str = Field(..., description="User email address")
    full_name: str = Field(..., min_length=2, max_length=100, description="User full name")
    password: str | None = Field(None, min_length=8, description="User password (auto-generated if not provided)")
    role: UserRole = Field(UserRole.USER, description="User role")


class UpdateUserRequest(BaseModel):
    email: str | None = Field(None, description="User email address")
    full_name: str | None = Field(None, min_length=2, max_length=100, description="User full name")


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


# API Routes
@app.get("/users")
@login_required
def list_users(
    role: Annotated[UserRole | None, Query] = None,
    limit: Annotated[int, Query] = 50,
    direction: Annotated[str, Query] = "desc",
    cursor: Annotated[str, Query] = None,
):
    # Create DTO
    dto = ListUsersDTO(
        role=role,
        limit=limit,
        direction=direction,
        cursor=cursor,
    )

    # Execute use case
    result = use_cases.list_users(dto)

    # Return response
    return result.model_dump(), HTTPStatus.OK


@app.get("/auth/me")
@login_required
def get_me():
    # Get user ID from auth context
    user_id = app.auth_context.user_id

    # Get user profile
    profile = use_cases.get_user(user_id)

    return profile.model_dump(), HTTPStatus.OK


@app.get("/users/<user_id>")
@admin_required
def get_user(user_id: str):
    # Execute use case
    profile = use_cases.get_user(user_id)

    # Return response
    return profile.model_dump(), HTTPStatus.OK


@app.post("/users")
@admin_required
def create_user(request: CreateUserRequest):
    # Execute use case
    dto = CreateUserDTO(
        email=request.email,
        full_name=request.full_name,
        password=request.password,
        role=request.role,
    )
    user = use_cases.create_user(dto)

    # Return profile (without password_hash)
    profile = UserProfile.from_user(user)

    return profile.model_dump(), HTTPStatus.CREATED


@app.put("/users/<user_id>")
@login_required
def update_user(user_id: str, request: UpdateUserRequest):
    # Verify permission (self or admin)
    if not app.auth_context.is_admin() and app.auth_context.user_id != user_id:
        raise AdminRequiredError("You can only update your own profile")

    # Execute use case
    dto = UpdateUserDTO(
        user_id=user_id,
        email=request.email,
        full_name=request.full_name,
    )
    use_cases.update_user(dto)

    return None, HTTPStatus.NO_CONTENT


@app.put("/users/<user_id>/change-password")
@login_required
def change_password(user_id: str, request: ChangePasswordRequest):
    # Verify user is changing their own password
    if app.auth_context.user_id != user_id:
        raise CrossUserAccessError("You can only change your own password")

    # Execute use case
    dto = ChangePasswordDTO(
        user_id=user_id,
        current_password=request.current_password,
        new_password=request.new_password,
    )
    use_cases.change_password(dto)

    # Return 204 No Content
    return None, HTTPStatus.NO_CONTENT


@app.delete("/users/<user_id>")
@admin_required
def delete_user(user_id: str):
    # Execute use case (includes self-delete check)
    use_cases.delete_user(user_id, requesting_user_id=app.auth_context.user_id)

    # Return 204 No Content
    return None, HTTPStatus.NO_CONTENT


# Lambda handler
def handler(event: dict, context: LambdaContext) -> dict:
    """Lambda function handler for users endpoints."""
    return app.resolve(event, context)
