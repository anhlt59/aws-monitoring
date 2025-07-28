from src.adapters.db.models.base import DynamoModel
from src.models import BaseModel


class BaseMapper[P: DynamoModel, M: BaseModel]:
    @classmethod
    def to_persistence(cls, model: M) -> P:
        raise NotImplementedError

    @classmethod
    def to_model(cls, persistence: P) -> M:
        raise NotImplementedError
