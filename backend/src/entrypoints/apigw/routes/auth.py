"""Authentication API Gateway handlers."""

from http import HTTPStatus

from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel, Field

from src.domain.models.user import UserProfile
from src.domain.use_cases.auth import (
    AuthenticateUser,
    AuthenticateUserDTO,
    GenerateAuthTokens,
    LogoutUser,
    LogoutUserDTO,
    RefreshAuthToken,
    RefreshTokenDTO,
)
from src.entrypoints.apigw.base import create_app
from src.entrypoints.apigw.configs import CORS_ALLOW_ORIGIN, CORS_MAX_AGE

# Create app
app = create_app(
    cors_allow_origin=CORS_ALLOW_ORIGIN,
    cors_max_age=CORS_MAX_AGE,
)

# Initialize use cases
authenticate_user_uc = AuthenticateUser()
generate_tokens_uc = GenerateAuthTokens()
refresh_token_uc = RefreshAuthToken()
logout_user_uc = LogoutUser()


# Request/Response models
class LoginRequest(BaseModel):
    """Login request model."""

    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")
    remember_me: bool = Field(default=False, description="Extend token expiration to 30 days")


class LoginResponse(BaseModel):
    """Login response model."""

    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserProfile


class RefreshRequest(BaseModel):
    """Refresh token request model."""

    refresh_token: str = Field(..., description="JWT refresh token")


class RefreshResponse(BaseModel):
    """Refresh token response model."""

    access_token: str
    token_type: str
    expires_in: int


# API Routes
@app.post("/auth/login")
def login(login_request: LoginRequest):
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
    user_profile = UserProfile.from_user(user)

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
def refresh_token(refresh_request: RefreshRequest):
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
def logout():
    """
    User logout endpoint.

    Invalidate current access token (client-side).
    """
    # Get auth context (validates token)
    # auth = get_auth_context(app)

    # Extract token from header (for potential blacklisting)
    auth_header = app.current_event.headers.get("Authorization")
    token = auth_header.split()[1] if auth_header else ""

    # Logout (currently a no-op, handled client-side)
    logout_dto = LogoutUserDTO(access_token=token)
    logout_user_uc.execute(logout_dto)

    # Return 204 No Content
    return None, HTTPStatus.NO_CONTENT


# Lambda handler
def handler(event: dict, context: LambdaContext) -> dict:
    """Lambda function handler for auth endpoints."""
    return app.resolve(event, context)
