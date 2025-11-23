"""Users API Gateway handlers."""

from http import HTTPStatus
from typing import Annotated

from aws_lambda_powertools.event_handler.openapi.params import Query
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel, Field

from src.domain.models.user import UserRole
from src.domain.use_cases.users import (
    ChangePassword,
    ChangePasswordDTO,
    CreateUser,
    CreateUserDTO,
    DeleteUser,
    GetUser,
    ListUsers,
    ListUsersDTO,
    UpdateUser,
    UpdateUserDTO,
)
from src.entrypoints.apigw.base import create_app
from src.entrypoints.apigw.configs import CORS_ALLOW_ORIGIN, CORS_MAX_AGE
from src.entrypoints.apigw.middleware.auth import get_auth_context, verify_user_or_admin

# Create app
app = create_app(
    cors_allow_origin=CORS_ALLOW_ORIGIN,
    cors_max_age=CORS_MAX_AGE,
)

# Initialize use cases
create_user_uc = CreateUser()
get_user_uc = GetUser()
list_users_uc = ListUsers()
update_user_uc = UpdateUser()
change_password_uc = ChangePassword()
delete_user_uc = DeleteUser()


# Request/Response models
class CreateUserRequest(BaseModel):
    """Create user request model."""

    email: str = Field(..., description="User email address")
    full_name: str = Field(..., min_length=2, max_length=100, description="User full name")
    password: str | None = Field(None, min_length=8, description="User password (auto-generated if not provided)")
    role: UserRole = Field(UserRole.USER, description="User role")


class UpdateUserRequest(BaseModel):
    """Update user request model."""

    email: str | None = Field(None, description="User email address")
    full_name: str | None = Field(None, min_length=2, max_length=100, description="User full name")
    role: UserRole | None = Field(None, description="User role")


class ChangePasswordRequest(BaseModel):
    """Change password request model."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


# API Routes
@app.get("/users")
def list_users(
    role: Annotated[UserRole | None, Query] = None,
    search: Annotated[str | None, Query] = None,
    page: Annotated[int, Query] = 1,
    page_size: Annotated[int, Query] = 20,
):
    """
    List users endpoint.

    Requires admin role.
    Supports filtering by role and email search.
    """
    # Get auth context and check admin
    auth = get_auth_context(app)
    if not auth.is_admin():
        from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

        raise UnauthorizedError("Admin role required to list users")

    # Create DTO
    dto = ListUsersDTO(
        role=role,
        search=search,
        page=page,
        page_size=page_size,
    )

    # Execute use case
    result = list_users_uc.execute(dto)

    # Return response
    return {
        "items": [profile.model_dump() for profile in result.items],
        "total": result.total,
        "page": result.page,
        "page_size": result.page_size,
        "has_more": result.has_more,
    }, HTTPStatus.OK


@app.get("/users/<user_id>")
def get_user(user_id: str):
    """
    Get user by ID endpoint.

    Users can view their own profile, admins can view any profile.
    """
    # Get auth context
    auth = get_auth_context(app)

    # Verify permission (self or admin)
    verify_user_or_admin(app, user_id)

    # Execute use case
    profile = get_user_uc.execute(user_id)

    # Return response
    return profile.model_dump(), HTTPStatus.OK


@app.post("/users")
def create_user(request: CreateUserRequest):
    """
    Create user endpoint.

    Requires admin role.
    """
    # Get auth context and check admin
    auth = get_auth_context(app)
    if not auth.is_admin():
        from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

        raise UnauthorizedError("Admin role required to create users")

    # Create DTO
    dto = CreateUserDTO(
        email=request.email,
        full_name=request.full_name,
        password=request.password,
        role=request.role,
    )

    # Execute use case
    user = create_user_uc.execute(dto)

    # Return profile (without password_hash)
    from src.domain.models.user import UserProfile

    profile = UserProfile.from_user(user)

    return profile.model_dump(), HTTPStatus.CREATED


@app.put("/users/<user_id>")
def update_user(user_id: str, request: UpdateUserRequest):
    """
    Update user endpoint.

    Users can update their own profile, admins can update any profile.
    """
    # Get auth context
    auth = get_auth_context(app)

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
