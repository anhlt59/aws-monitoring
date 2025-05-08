from pydantic import BaseModel, Field
from uuid_utils import uuid7

from src.common.utils.datetime_utils import current_utc_timestamp


# Model
class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid7()))
    name: str
    description: str
    created_at: int = Field(default_factory=current_utc_timestamp)
    updated_at: int = Field(default_factory=current_utc_timestamp)


# Request DTOs
class ProjectCreateDTO(BaseModel):
    name: str
    description: str | None = None


class ProjectUpdateDTO(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectListDTO(BaseModel):
    limit: int = 20
    cursor: str | None = None
    name_prefix: str | None = None
    direction: str | None = "asc"


# Response DTOs
class ProjectItemDTO(BaseModel):
    name: str
    description: str
    created_at: int
    updated_at: int


class ProjectPaginatedDTO(BaseModel):
    items: list[ProjectItemDTO]
    limit: int = 20
    next: str | None = None
    previous: str | None = None
