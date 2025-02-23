import json
from datetime import date, datetime
from functools import wraps
from typing import Iterable, List, Type, TypeVar

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.base import SingletonMeta
from src.constants import COMPRESS_SIZE, DATETIME_FORMAT, DB_URI
from src.logger import logger
from src.models.base import BaseModel
from src.types import SqsMessage
from src.utils import chunks

SqlT = TypeVar("SqlT", bound=BaseModel)
engine = create_engine(
    DB_URI,
    poolclass=NullPool,
    connect_args={"connect_timeout": 900},
    isolation_level="READ COMMITTED",
)
Session = sessionmaker(bind=engine, autoflush=False)
session: Session


def get_connection() -> Session:
    global session
    if "session" not in globals() or session.is_active is False:
        session = Session(autocommit=False)
        session.info["in_transaction"] = False
    return session


def transaction(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        global session
        if session.info["in_transaction"]:
            # if this transaction is nested in another transaction
            return func(*args, **kwargs)
        else:
            session.info["in_transaction"] = True
            try:
                result = func(*args, **kwargs)
                session.commit()
                session.info["in_transaction"] = False
                return result
            except Exception as e:
                session.rollback()
                session.info["in_transaction"] = False
                raise e

    return decorator


class SqlRepository(metaclass=SingletonMeta):
    model_class: Type[SqlT]
    logger = logger
    session: Session

    __slots__ = ("session", "model_class")

    def __init__(self):
        self.session = get_connection()

    @property
    def query(self):
        return self.session.query(self.model_class)

    @query.setter
    def query(self, value):
        raise AttributeError("self.query is a concrete attribute; use self.session.query instead.")

    def _filter(self, *args, **kwargs):
        query = self.query
        if args:
            query = query.filter(*args)
        if kwargs:
            query = query.filter_by(**kwargs)
        return query

    def get(self, pk) -> SqlT:
        return self.session.get(self.model_class, pk)

    def get_by(self, *args, **kwargs):
        return self._filter(*args, **kwargs).first()

    def list(self, *args, offset: int = 0, limit: int | None = None, **kwargs) -> List[SqlT]:
        return self._filter(*args, **kwargs).offset(offset).limit(limit).all()

    @transaction
    def create(self, item: dict | None = None, model: SqlT | None = None) -> SqlT:
        if model is None:
            model = self.model_class(**item)
        self.session.add(model)
        if not self.session.info["in_transaction"]:
            self.session.commit()
        return model

    @transaction
    def bulk_create(
        self, items: List[dict] | None = None, models: List[SqlT] | None = None, return_defaults: bool = False
    ) -> List[SqlT]:
        if models is None:
            models = [self.model_class(**item) for item in items]
        self.session.bulk_save_objects(models, return_defaults=return_defaults)
        if not self.session.info["in_transaction"]:
            self.session.commit()
        return models

    @transaction
    def update(self, pk: str, fields: dict) -> SqlT:
        model = self.session.get(self.model_class, pk)
        for key, value in fields.items():
            setattr(model, key, value)
        self.session.commit()
        return model

    @transaction
    def bulk_update(self, items: List[dict] | None = None, models: List[SqlT] | None = None) -> List[SqlT]:
        if models:
            self.session.bulk_save_objects(models)
        if items:
            self.session.bulk_update_mappings(self.model_class, items)
        if not self.session.info["in_transaction"]:
            self.session.commit()
        return models

    @transaction
    def save(self, model: SqlT) -> SqlT:
        self.session.add(model)
        if not self.session.info["in_transaction"]:
            self.session.commit()
        return model

    @transaction
    def delete(self, model) -> None:
        self.session.delete(model)
        if not self.session.info["in_transaction"]:
            self.session.commit()

    @transaction
    def delete_all(self) -> None:
        self.session.query(self.model_class).delete()
        if not self.session.info["in_transaction"]:
            self.session.commit()


class SqlExtendedRepository(SqlRepository):
    @classmethod
    def deserialize_sqs_record(cls, record) -> Iterable[SqlT]:
        try:
            # parse JSON
            items = json.loads(record.get("body", "null"))
        except Exception as e:
            cls.logger.error(f"Failed to parse JSON {record}: {e}")
            raise e
        else:
            if not isinstance(items, list):
                raise TypeError(f"Valid type is `list`, got `{type(items)}` instead")

            # deserialize item
            for item in items:
                try:
                    model = cls.model_class.deserialize(item)
                    # logger.debug(f"Deserialized {model}: {item}")
                    yield model
                except Exception as e:
                    cls.logger.error(f"Failed to deserialize record {record}: {e}")

    @classmethod
    def default_serializer(cls, _obj):
        if isinstance(_obj, datetime) or isinstance(_obj, date):
            return _obj.strftime(DATETIME_FORMAT)
        elif isinstance(_obj, BaseModel):
            return _obj.to_dict()

    @classmethod
    def to_json(cls, items: Iterable[SqlT], default=None) -> Iterable[str] | str:
        return json.dumps(items, default=default or cls.default_serializer)

    message_serializer = default_serializer

    @classmethod
    def to_sqs_messages(
        cls, items: Iterable[SqlT], compress_size: int = COMPRESS_SIZE, message_attributes=None
    ) -> Iterable[SqsMessage]:
        for chunk in chunks(items, compress_size):
            yield SqsMessage(
                message_body=cls.to_json(chunk, cls.message_serializer),
                message_attributes=message_attributes or {},
            )
