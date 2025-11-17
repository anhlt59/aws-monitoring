from typing import Generic, TypeVar

from pydantic import BaseModel, Field

M = TypeVar("M", bound=BaseModel)


class Page(BaseModel, Generic[M]):
    items: list[M] = Field(alias="Items", default_factory=list)
    limit: int = Field(alias="MaxResults", default=20)
    next: str | None = Field(alias="NextToken", default=None)
    previous: str | None = Field(alias="PreviousToken", default=None)

    @property
    def total(self):
        return len(self.items)
