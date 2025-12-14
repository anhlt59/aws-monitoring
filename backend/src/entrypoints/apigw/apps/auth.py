from http import HTTPStatus

from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel

from src.adapters.db.repositories import UserRepository
from src.domain.iam.models import UserProfile
from src.domain.iam.use_cases.auth import AuthenticateUserDTO, AuthUseCases, LogoutUserDTO, RefreshTokenDTO
from src.entrypoints.apigw.base import create_app, jwt_service, login_required

# ------------------------------
# Initialization
# ------------------------------
use_cases = AuthUseCases(user_repository=UserRepository(), jwt_service=jwt_service)
app = create_app()


# ------------------------------
# Request/Response models
# ------------------------------
class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserProfile


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


# ------------------------------
# API Routes
# ------------------------------
@app.post("/auth/login")
def login(login_request: AuthenticateUserDTO):
    # Authenticate user
    user = use_cases.authenticate_user(dto=login_request)

    # Generate tokens
    tokens = use_cases.generate_auth_tokens(user)

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
def refresh_token(refresh_request: RefreshTokenDTO):
    # Refresh token
    new_token = use_cases.refresh_auth_token(dto=refresh_request)

    # Return response
    response = RefreshResponse.model_validate(new_token)

    return response.model_dump(), HTTPStatus.OK


@app.post("/auth/logout")
@login_required
def logout():
    # Extract token from header (for potential blacklisting)
    auth_header = app.current_event.headers.get("Authorization")

    # Logout (currently a no-op, handled client-side)
    logout_dto = LogoutUserDTO(access_token=auth_header)
    use_cases.logout_user(logout_dto)

    # Return 204 No Content
    return None, HTTPStatus.NO_CONTENT


# ------------------------------
# Lambda Handler
# ------------------------------
def handler(event: dict, context: LambdaContext):
    """Lambda function handler for auth endpoints."""
    return app.resolve(event, context)
