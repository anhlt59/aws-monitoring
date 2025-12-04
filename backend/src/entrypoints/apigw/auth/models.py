from pydantic import BaseModel, Field

from src.domain.models.user import UserProfile


# Request/Response models
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
