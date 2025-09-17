from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

M = TypeVar("M", bound=BaseModel)


class PaginatedRequest(BaseModel):
    """Base model for paginated requests"""

    model_config = ConfigDict(extra="ignore", use_enum_values=True, str_strip_whitespace=True)

    limit: int = Field(default=50, ge=10, le=100, description="Number of items per page")
    direction: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort direction")
    cursor: str | None = Field(default=None, description="Pagination cursor")


class PaginatedResponse(BaseModel, Generic[M]):
    """Base model for paginated responses"""

    items: list[M] = Field(..., description="List of items")
    limit: int = Field(..., description="Items per page")
    next: str | None = Field(default=None, description="Next page cursor")
    previous: str | None = Field(default=None, description="Previous page cursor")
    total: int | None = Field(default=None, description="Total number of items (if available)")
