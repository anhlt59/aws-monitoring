from typing import Any, Generic, List, Sequence, Type, TypeVar

from pydantic import BaseModel
from pynamodb.attributes import Attribute
from pynamodb.exceptions import DeleteError, DoesNotExist, GetError, PutError, QueryError
from pynamodb.models import Action, Condition, Index, ResultIterator

from src.adapters.db.models.base import DynamoModel
from src.common.exceptions.http import InternalServerError, NotFoundError, UnprocessedError

M = TypeVar("M", bound=BaseModel)


class QueryResult(BaseModel, Generic[M]):
    items: list[M]
    limit: int = 50
    cursor: dict | None = None


class DynamoRepository[M: DynamoModel]:
    model_cls: Type[M]
    hash_key_attr: Attribute
    range_key_attr: Attribute

    def __init__(self):
        self.hash_key_attr = self.model_cls.pk
        self.range_key_attr = self.model_cls.sk

    # Generic operation methods -------------------------------------------------
    def _get(self, hash_key: Any, range_key: Any = None, attributes_to_get: List[str] | None = None) -> M:
        try:
            return self.model_cls.get(hash_key, range_key=range_key, attributes_to_get=attributes_to_get)
        except DoesNotExist as err:
            raise NotFoundError(f"{self.__class__.__name__}: {err}")
        except GetError as err:
            raise UnprocessedError(f"{self.__class__.__name__}: {err}")
        except Exception as err:
            raise InternalServerError(f"{self.__class__.__name__}: {err}")

    def _query(
        self,
        hash_key: Any,
        range_key_condition: Condition | None = None,
        index: Index | None = None,
        scan_index_forward: bool | None = None,
        filter_condition: Condition | None = None,
        attributes_to_get: List[str] | None = None,
        last_evaluated_key: dict[str, dict[str, Any]] | None = None,
        limit: int = 50,
    ) -> ResultIterator[M]:
        query_cls = index if index is not None else self.model_cls
        try:
            return query_cls.query(
                hash_key,
                range_key_condition=range_key_condition,
                filter_condition=filter_condition,
                attributes_to_get=attributes_to_get,
                last_evaluated_key=last_evaluated_key,
                limit=limit,
                scan_index_forward=scan_index_forward,
            )
        except QueryError as err:
            raise UnprocessedError(f"{self.__class__.__name__}: {err}")
        except Exception as err:
            raise InternalServerError(f"{self.__class__.__name__}: {err}")

    def _create(self, model: M, condition: Condition | None = None):
        condition &= self.hash_key_attr.does_not_exist()
        if self.range_key_attr is not None:
            condition &= self.range_key_attr.does_not_exist()

        try:
            model.save(condition=condition)
        except PutError as err:
            raise UnprocessedError(f"{self.__class__.__name__}: {err}")
        except Exception as err:
            raise InternalServerError(f"{self.__class__.__name__}: {err}")

    def _update(
        self,
        hash_key: Any,
        range_key: Any = None,
        attributes: dict | None = None,
        actions: Sequence[Action] | None = None,
        condition: Condition | None = None,
    ):
        # build actions
        actions = list(actions) if actions else []
        if attributes is not None:
            for key, value in attributes.items():
                if attr := getattr(self.model_cls, key):
                    actions.append(attr.set(value))
                else:
                    raise ValueError(f"{self.__class__.__name__}: Attribute {key} does not exist")

        # raise error if item does not exist
        condition &= self.hash_key_attr.exists()
        if self.range_key_attr is not None:
            condition &= self.range_key_attr.exists()

        model = self.model_cls(hash_key=hash_key, range_key=range_key)

        try:
            model.update(actions=actions, condition=condition)
        except PutError as err:
            raise UnprocessedError(f"{self.__class__.__name__}: {err}")
        except Exception as err:
            raise InternalServerError(f"{self.__class__.__name__}: {err}")

    def _delete(
        self,
        hash_key: Any,
        range_key: Any = None,
        condition: Condition | None = None,
    ):
        # raise error if item does not exist
        condition &= self.hash_key_attr.exists()
        if self.range_key_attr is not None:
            condition &= self.range_key_attr.exists()

        model = self.model_cls(hash_key=hash_key, range_key=range_key)

        try:
            model.delete(condition=condition)
        except DeleteError as err:
            raise UnprocessedError(f"{self.__class__.__name__}: {err}")
        except Exception as err:
            raise InternalServerError(f"{self.__class__.__name__}: {err}")

    def _count(
        self,
        hash_key: Any,
        range_key_condition: Condition | None = None,
        filter_condition: Condition | None = None,
        index: Index | None = None,
    ) -> int:
        query_cls = index if index is not None else self.model_cls

        try:
            return query_cls.count(hash_key, range_key_condition, filter_condition=filter_condition)
        except QueryError as err:
            raise UnprocessedError(f"{self.__class__.__name__}: {err}")
        except Exception as err:
            raise InternalServerError(f"{self.__class__.__name__}: {err}")
