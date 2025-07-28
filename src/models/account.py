from pydantic import BaseModel, Field

from src.common.utils.datetime_utils import current_utc_timestamp


# Model
class Account(BaseModel):
    id: str
    name: str
    stage: str
    region: str
    deployed_at: int
    created_at: int = Field(default_factory=current_utc_timestamp)


# DTOs
class UpdateAccountDTO(BaseModel):
    name: str | None = None
    stage: str | None = None
    region: str | None = None
    deployed_at: int | None = None
