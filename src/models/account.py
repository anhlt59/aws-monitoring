from pydantic import BaseModel, Field

from src.common.utils.datetime_utils import current_utc_timestamp


# Model
class Account(BaseModel):
    id: str
    region: str
    status: str | None = None
    deployed_at: int
    created_at: int = Field(default_factory=current_utc_timestamp)

    @property
    def persistence_id(self) -> str:
        return self.id


# DTOs
class UpdateAccountDTO(BaseModel):
    region: str | None = None
    status: str | None = None
    deployed_at: int | None = None
