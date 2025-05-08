# from typing import Any, Generic, TypeVar

# from pydantic import BaseModel, ConfigDict, Field
# from uuid_utils import uuid7

# from src.common.utils.datetime_utils import current_utc_timestamp


# class Model(BaseModel):
#     model_config = ConfigDict(from_attributes=True, use_enum_values=True, validate_assignment=True)
#     # Attributes
#     id: str = Field(default_factory=lambda: str(uuid7()))
#     created_at: int = Field(default_factory=current_utc_timestamp)
#     updated_at: int = Field(default_factory=current_utc_timestamp)


# M = TypeVar("M", bound=BaseModel)


# class PaginatedInputDTO(BaseModel):
#     model_config = ConfigDict(use_enum_values=True, str_strip_whitespace=True)
#     # Attributes
#     limit: int = 20
#     cursor: str | None = None
#     direction: str | None = "asc"


# class PaginatedOutputDTO(BaseModel, Generic[M]):
#     model_config = ConfigDict(use_enum_values=True, str_strip_whitespace=True)
#     # Attributes
#     items: list[M]
#     limit: int = 20
#     next: str | None = None
#     previous: str | None = None
