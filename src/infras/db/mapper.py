from typing import Protocol

from pydantic import BaseModel as EntityModel

from src.infras.db.models import DynamoModel as PersistenceModel


class Mapper[P: PersistenceModel, E: EntityModel](Protocol):
    @classmethod
    def to_persistence(cls, model: E) -> P: ...

    @classmethod
    def to_entity(cls, persistence: P) -> E: ...
