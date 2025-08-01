from typing import Protocol

from src.adapters.db.models.base import DynamoModel
from src.models import BaseModel


class Mapper[P: DynamoModel, M: BaseModel](Protocol):
    @classmethod
    def to_persistence(cls, model: M) -> P: ...

    @classmethod
    def to_model(cls, persistence: P) -> M: ...
