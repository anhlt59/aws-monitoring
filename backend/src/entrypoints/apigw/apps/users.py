"""Users API Gateway handlers."""

from http import HTTPStatus
from typing import Annotated

from aws_lambda_powertools.event_handler.openapi.params import Query
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel, Field

from entrypoints.apigw.base import admin_required
from src.adapters.db.repositories import UserRepository
from src.common.exceptions import UnauthorizedError
from src.domain.iam.use_cases.user import ChangePasswordDTO, CreateUserDTO, ListUsersDTO, UserUseCases
from src.domain.models.user import UserProfile, UserRole
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
    role: UserRole | None = Field(None, description="User role")


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


# API Routes
@app.get("/users")
@login_required
def list_users(
    role: Annotated[UserRole | None, Query] = None,
    email_startswith: Annotated[str | None, Query] = None,
    limit: Annotated[int, Query] = 50,
    direction: Annotated[str, Query] = "desc",
    cursor: Annotated[str, Query] = None,
):
    # Get auth context and check admin
    if not app.auth_context.is_admin():
        raise UnauthorizedError("Admin role required to all users")

    # Create DTO
    dto = ListUsersDTO(
        role=role,
        email_startswith=email_startswith,
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
    # Get auth context
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
    # Get auth context and check admin
    if not app.auth_context.is_admin():
        raise UnauthorizedError("Admin role required to create users")

    # Create DTO
    dto = CreateUserDTO(
        email=request.email,
        full_name=request.full_name,
        password=request.password,
        role=request.role,
    )

    # Execute use case
    user = use_cases.create_user(dto)

    # Return profile (without password_hash)
    profile = UserProfile.from_user(user)

    return profile.model_dump(), HTTPStatus.CREATED


@app.put("/users/<user_id>")
def update_user(user_id: str, request: UpdateUserRequest):
    """
    Update user endpoint.

    Users can update their own profile, admins can update any profile.
    """

    # Verify permission (self or admin)
    verify_user_or_admin(app, user_id)

    # Create DTO
    dto = UpdateUserDTO(
        user_id=user_id,
        email=request.email,
        full_name=request.full_name,
        role=request.role,
    )

    # Execute use case
    user = update_user_uc.execute(dto)

    # Return profile
    from src.domain.models.user import UserProfile

    profile = UserProfile.from_user(user)

    return profile.model_dump(), HTTPStatus.OK


@app.put("/users/<user_id>/change-password")
def change_password(user_id: str, request: ChangePasswordRequest):
    """
    Change password endpoint.

    Users can only change their own password.
    """
    # Get auth context
    auth = get_auth_context(app)

    # Verify user is changing their own password
    if auth.user_id != user_id:
        from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

        raise UnauthorizedError("You can only change your own password")

    # Create DTO
    dto = ChangePasswordDTO(
        user_id=user_id,
        current_password=request.current_password,
        new_password=request.new_password,
    )

    # Execute use case
    change_password_uc.execute(dto)

    # Return 204 No Content
    return None, HTTPStatus.NO_CONTENT


@app.delete("/users/<user_id>")
def delete_user(user_id: str):
    """
    Delete user endpoint.

    Requires admin role. Cannot delete self.
    """
    # Get auth context and check admin
    auth = get_auth_context(app)
    if not auth.is_admin():
        from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

        raise UnauthorizedError("Admin role required to delete users")

    # Execute use case (includes self-delete check)
    delete_user_uc.execute(user_id, requesting_user_id=auth.user_id)

    # Return 204 No Content
    return None, HTTPStatus.NO_CONTENT


# Lambda handler
def handler(event: dict, context: LambdaContext) -> dict:
    """Lambda function handler for users endpoints."""
    return app.resolve(event, context)
