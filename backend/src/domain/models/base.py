from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

M = TypeVar("M", bound=BaseModel)


class PaginatedInputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", use_enum_values=True, str_strip_whitespace=True)
    # Attributes
    limit: int = Field(default=50, ge=10, le=100)
    direction: str = "desc"
    cursor: str | None = None


class PaginatedOutputDTO(BaseModel, Generic[M]):
    # Attributes
    items: list[M]
    limit: int = 50
    next: str = None
    previous: str = None


class QueryResult(BaseModel, Generic[M]):
    """Generic query result with pagination support.

    Attributes:
        items: List of domain model instances returned by the query
        limit: Maximum number of items per page
        cursor: Opaque cursor for pagination (implementation-specific)
    """

    items: list[M]
    limit: int = 50
    cursor: dict | None = None
