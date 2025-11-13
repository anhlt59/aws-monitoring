from pydantic import BaseModel, Field

from src.common.utils.datetime_utils import current_utc_timestamp

from .base import PaginatedInputDTO, QueryResult


# Model
class Context(BaseModel):
    """Domain model for system context information"""

    id: str  # Unique identifier (e.g., "backend-architecture", "database-schema")
    context_type: str  # Type: backend/database/api/architecture/infrastructure/deployment
    title: str  # Human-readable title
    content: dict  # Structured context information
    version: str = "1.0"  # Version for tracking updates
    created_at: int = Field(default_factory=current_utc_timestamp)
    updated_at: int = Field(default_factory=current_utc_timestamp)

    @property
    def persistence_id(self) -> str:
        return f"{self.context_type}#{self.id}"


# DTOs
class ListContextsDTO(PaginatedInputDTO):
    context_type: str | None = None


# Query Results
ContextQueryResult = QueryResult[Context]
