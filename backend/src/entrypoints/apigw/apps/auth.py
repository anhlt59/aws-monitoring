"""Authentication API Gateway handlers."""

from http import HTTPStatus

from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel, Field

from src.adapters.db.repositories import UserRepository
from src.domain.models.user import UserProfile
from src.entrypoints.apigw.base import create_app, login_required

user_repository = UserRepository()
app = create_app()


# ------------------------------
# Request/Response models
# ------------------------------
class LoginRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")
    remember_me: bool = Field(default=False, description="Extend token expiration to 30 days")


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserProfile


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="JWT refresh token")


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


# ------------------------------
# API Routes
# ------------------------------


@app.post("/auth/login")
def login(
    login_request: LoginRequest,
    authenticate_user_uc=Provide[Container.authenticate_user_uc],
    generate_tokens_uc=Provide[Container.generate_tokens_uc],
):
    """
    User login endpoint.
    Authenticate user with email and password, return JWT tokens.
    """
    # Authenticate user
    auth_dto = AuthenticateUserDTO(
        email=login_request.email,
        password=login_request.password,
    )
    user = authenticate_user_uc.execute(auth_dto)

    # Generate tokens
    tokens = generate_tokens_uc.execute(user, remember_me=login_request.remember_me)

    # Convert user to profile (exclude password_hash)
    user_profile = UserProfile.model_validate(user)

    # Return response
    response = LoginResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in,
        user=user_profile,
    )

    return response.model_dump(), HTTPStatus.OK


@app.post("/auth/refresh")
@login_required
def refresh_token(
    refresh_request: RefreshRequest,
    refresh_token_uc=Provide[Container.refresh_token_uc],
):
    """
    Refresh access token endpoint.
    Use refresh token to obtain a new access token.
    """
    # Refresh token
    refresh_dto = RefreshTokenDTO(refresh_token=refresh_request.refresh_token)
    new_token = refresh_token_uc.execute(refresh_dto)

    # Return response
    response = RefreshResponse(
        access_token=new_token.access_token,
        token_type=new_token.token_type,
        expires_in=new_token.expires_in,
    )

    return response.model_dump(), HTTPStatus.OK


@app.post("/auth/logout")
@login_required
def logout():
    # Get auth context (validates token)
    # auth = get_auth_context(app)

    # Extract token from header (for potential blacklisting)
    auth_header = app.current_event.headers.get("Authorization")
    token = auth_header.split()[1] if auth_header else ""

    # Logout (currently a no-op, handled client-side)
    logout_dto = LogoutUserDTO(access_token=token)
    # logout_user_uc.execute(logout_dto)

    # Return 204 No Content
    return None, HTTPStatus.NO_CONTENT


def handler(event: dict, context: LambdaContext):
    """Lambda function handler for auth endpoints."""
    return app.resolve(event, context)
